import os
import config

def generate_txt_report(
    filename: str,
    original_stats: dict,
    final_stats: dict,
    detected_issues: dict,
    cleaning_logs: list[str],
    ai_explanation: dict
) -> str:
    """
    Generates a structured text cleaning report file and saves it in config.REPORT_FOLDER.
    Returns path to generated report.
    """
    report_filename = f"report_{os.path.splitext(filename)[0]}.txt"
    report_path = os.path.join(config.REPORT_FOLDER, report_filename)

    lines = []
    lines.append("================================================================================")
    lines.append("                        DATA CLEANING AI AGENT REPORT                           ")
    lines.append("================================================================================")
    lines.append(f" Dataset Filename  : {filename}")
    lines.append("================================================================================")
    lines.append("")
    lines.append("1. DATASET OVERVIEW & BEFORE / AFTER COMPARISON")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f" Metric                   BEFORE              AFTER               CHANGE")
    lines.append("--------------------------------------------------------------------------------")
    
    orig_rows = original_stats.get('rows', 0)
    fin_rows = final_stats.get('rows', 0)
    lines.append(f" Total Rows               {orig_rows:<18} {fin_rows:<18} {fin_rows - orig_rows}")

    orig_cols = original_stats.get('columns', 0)
    fin_cols = final_stats.get('columns', 0)
    lines.append(f" Total Columns            {orig_cols:<18} {fin_cols:<18} {fin_cols - orig_cols}")

    orig_miss = original_stats.get('total_missing', 0)
    fin_miss = final_stats.get('total_missing', 0)
    lines.append(f" Missing Values           {orig_miss:<18} {fin_miss:<18} {fin_miss - orig_miss}")

    orig_dup = original_stats.get('duplicates', 0)
    fin_dup = final_stats.get('duplicates', 0)
    lines.append(f" Duplicate Rows           {orig_dup:<18} {fin_dup:<18} {fin_dup - orig_dup}")

    orig_out = original_stats.get('total_outliers', 0)
    fin_out = final_stats.get('total_outliers', 0)
    lines.append(f" Numerical Outliers       {orig_out:<18} {fin_out:<18} {fin_out - orig_out}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("")
    
    lines.append("2. SUMMARY OF DETECTED DATA-QUALITY PROBLEMS")
    lines.append("--------------------------------------------------------------------------------")
    missing_by_col = detected_issues.get('missing_by_column', {})
    lines.append("Missing Values by Column:")
    for col, count in missing_by_col.items():
        if count > 0:
            lines.append(f"  • {col}: {count} missing value(s)")

    outliers_by_col = detected_issues.get('outliers_by_column', {})
    lines.append("Numerical Outliers by Column:")
    if outliers_by_col:
        for col, info in outliers_by_col.items():
            lines.append(f"  • {col}: {info['count']} outlier(s) detected [bounds: {info['lower_bound']} to {info['upper_bound']}]")
    else:
        lines.append("  • None detected.")

    lines.append("")
    lines.append("3. CHRONOLOGICAL DATA CLEANING AUDIT LOG")
    lines.append("--------------------------------------------------------------------------------")
    if cleaning_logs:
        for idx, log_entry in enumerate(cleaning_logs, 1):
            lines.append(f"  {idx}. {log_entry}")
    else:
        lines.append("  No cleaning operations performed.")
    lines.append("")

    lines.append("4. AI DATASET QUALITY SUMMARY & EXPLANATION")
    lines.append("--------------------------------------------------------------------------------")
    summary = ai_explanation.get('summary', '')
    explanation = ai_explanation.get('explanation', '')
    recommendations = ai_explanation.get('recommendations', '')

    lines.append("Executive Summary:")
    lines.append(f"  {summary}")
    lines.append("")
    lines.append("Cleaning Rationale:")
    lines.append(f"  {explanation}")
    lines.append("")
    lines.append("Recommendations & Limitations:")
    lines.append(f"  {recommendations}")
    lines.append("================================================================================")
    lines.append(" End of Data Cleaning Agent Report")
    lines.append("================================================================================")

    report_content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path
