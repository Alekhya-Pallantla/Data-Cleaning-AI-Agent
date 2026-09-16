import os
import json

class ExplanationAgent:
    """
    Explanation Agent: Generates natural language dataset quality summaries,
    cleaning rationale, and recommendations.
    Uses LLM API if key is present; otherwise falls back to deterministic template engine.
    """
    def __init__(self, analysis_report: dict, validation_stats: dict, cleaning_logs: list[str]):
        self.analysis = analysis_report
        self.validation = validation_stats
        self.logs = cleaning_logs
        self.api_key = os.environ.get('OPENAI_API_KEY', '').strip()

    def generate_explanation(self) -> dict:
        if self.api_key and self.api_key != 'your_openai_api_key_here':
            try:
                return self._generate_with_llm()
            except Exception as e:
                # Fail gracefully back to template engine if API call fails
                return self._generate_with_template(fallback_reason=str(e))
        else:
            return self._generate_with_template()

    def _generate_with_template(self, fallback_reason: str = None) -> dict:
        """Rule-based intelligent template synthesis."""
        before = self.validation['before']
        after = self.validation['after']
        fixed = self.validation['fixed']

        # 1. Dataset Quality Summary
        rows = before['rows']
        cols = before['columns']
        missing = before['total_missing']
        dups = before['duplicates']
        outliers = before['total_outliers']
        quality_score = before['quality_score']
        after_score = after['quality_score']

        summary_parts = [
            f"The uploaded dataset contains {rows} rows and {cols} columns with an initial Data Quality Score of {quality_score}/100.",
            f"During analysis, the agent detected {missing} missing values, {dups} duplicate row(s), and {outliers} numerical outlier(s)."
        ]
        
        if after_score > quality_score:
            summary_parts.append(f"Following automated data cleaning, the dataset overall quality score improved to {after_score}/100.")
        
        summary_text = " ".join(summary_parts)

        # 2. Cleaning Rationale
        explanation_lines = []
        if fixed['missing_fixed'] > 0:
            explanation_lines.append(
                f"• Missing Values: Imputed {fixed['missing_fixed']} missing cell(s). Numerical columns used median imputation (robust against skewness) while categorical columns used mode imputation."
            )
        if fixed['duplicates_fixed'] > 0:
            explanation_lines.append(
                f"• Deduplication: Identified and dropped {fixed['duplicates_fixed']} duplicate record(s) to eliminate redundant observations while retaining the first occurrence."
            )
        if any('whitespace' in log.lower() for log in self.logs):
            explanation_lines.append(
                "• Text Normalization: Stripped leading/trailing whitespace and normalized text fields to eliminate accidental spacing inconsistencies."
            )
        if any('date' in log.lower() for log in self.logs):
            explanation_lines.append(
                "• Date Standardization: Parsed date columns across heterogeneous string formats and standardized them into uniform ISO (YYYY-MM-DD) format."
            )
        if any('outlier' in log.lower() for log in self.logs):
            if after['total_outliers'] > 0 and fixed['outliers_handled'] == 0:
                explanation_lines.append(
                    f"• Numerical Outliers: Detected {after['total_outliers']} potential outlier(s). Retained them per conservative policy to avoid destroying valid extreme domain measurements."
                )
            elif fixed['outliers_handled'] > 0:
                explanation_lines.append(
                    f"• Numerical Outliers: Capped or removed {fixed['outliers_handled']} numerical outlier(s) using Interquartile Range (IQR) threshold boundaries."
                )

        if not explanation_lines:
            explanation_text = "The dataset was already well-formatted. No critical cleaning actions were required."
        else:
            explanation_text = "\n".join(explanation_lines)

        # 3. Recommendations & Limitations
        rec_lines = []
        if after['total_outliers'] > 0:
            rec_lines.append(f"1. Review {after['total_outliers']} retained numerical outlier(s) with domain experts before feeding into predictive machine learning models.")
        if len(self.analysis.get('constant_columns', [])) > 0:
            const_cols = ", ".join(self.analysis['constant_columns'])
            rec_lines.append(f"2. Consider dropping constant column(s) [{const_cols}] if building machine learning models as they provide zero variance/information.")
        rec_lines.append("3. Verify date conversions for any custom localized formats before downstream analysis.")

        rec_text = "\n".join(rec_lines)

        result = {
            'summary': summary_text,
            'explanation': explanation_text,
            'recommendations': rec_text,
            'mode': 'template' if not fallback_reason else f'template (LLM fallback: {fallback_reason})'
        }
        return result

    def _generate_with_llm(self) -> dict:
        """Call OpenAI LLM API if key is available."""
        import urllib.request

        prompt = f"""You are an expert AI Data Science Assistant. Analyze the following data cleaning stats:
Dataset: {self.analysis['rows']} rows, {self.analysis['columns']} columns.
Initial Issues: {self.analysis['total_missing']} missing, {self.analysis['duplicate_rows']} duplicates, {self.analysis['total_outliers']} outliers.
Cleaning Actions Performed:
{json.dumps(self.logs, indent=2)}
Before/After Stats:
{json.dumps(self.validation, indent=2)}

Provide a JSON output with 3 keys:
"summary": Short high-level summary of dataset quality.
"explanation": Detailed explanation of what was changed and why.
"recommendations": Key actionable recommendations for the data analyst.
Return strictly valid JSON.
"""

        # Make simple urllib request to OpenAI API (to avoid extra mandatory SDK dependencies)
        req_data = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            content = res_json['choices'][0]['message']['content']
            parsed = json.loads(content)
            parsed['mode'] = 'llm'
            return parsed
