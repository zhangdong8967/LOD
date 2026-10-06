#!/usr/bin/env python3
"""
图表质量检查脚本 - Clinical Chemistry投稿要求
"""
import os
from pathlib import Path
from PIL import Image
import json

def check_figure_quality(figure_path):
    """检查单个图片的质量参数"""
    results = {
        "file": figure_path.name,
        "exists": figure_path.exists(),
        "checks": {}
    }
    
    if not figure_path.exists():
        results["checks"]["error"] = "File not found"
        return results
    
    try:
        with Image.open(figure_path) as img:
            dpi = img.info.get('dpi', (72, 72))
            results["checks"]["dpi"] = {
                "value": dpi,
                "pass": min(dpi) >= 300,
                "requirement": ">=300 dpi"
            }
            
            width, height = img.size
            results["checks"]["dimensions"] = {
                "value": f"{width}x{height}",
                "width_px": width,
                "height_px": height,
            }
            
            file_size_mb = figure_path.stat().st_size / (1024 * 1024)
            results["checks"]["file_size"] = {
                "value_mb": round(file_size_mb, 2),
                "pass": file_size_mb < 10,
                "requirement": "<10 MB"
            }
            
            results["checks"]["color_mode"] = {
                "value": img.mode,
                "pass": img.mode in ['RGB', 'RGBA', 'CMYK'],
                "requirement": "RGB/RGBA/CMYK"
            }
            
            fmt = img.format
            results["checks"]["format"] = {
                "value": fmt,
                "pass": fmt in ['PNG', 'TIFF', 'JPEG'],
                "requirement": "PNG/TIFF/JPEG",
                "recommendation": "TIFF for final submission"
            }
            
    except Exception as e:
        results["checks"]["error"] = str(e)
    
    return results


def check_all_figures(paper_artifacts_dir):
    """检查所有主文图表"""
    figures_dir = Path(paper_artifacts_dir) / "figures"
    
    main_figures = [
        "Fig1_Fig1-lod-replicate-planning.png",
        "Fig2_Fig2-tierA-calibration.png",
    ]
    
    results = {"timestamp": "2026-08-24", "figures": []}
    
    print("=" * 70)
    print("Clinical Chemistry 图表质量检查报告")
    print("=" * 70)
    
    for fig_name in main_figures:
        fig_path = figures_dir / fig_name
        result = check_figure_quality(fig_path)
        results["figures"].append(result)
        
        print(f"\n📊 {fig_name}")
        print("-" * 70)
        
        if not result["exists"]:
            print("❌ 文件不存在")
            continue
        
        if "error" in result["checks"]:
            print(f"❌ 错误: {result['checks']['error']}")
            continue
        
        for check_name, check_data in result["checks"].items():
            if check_name == "error":
                continue
                
            if isinstance(check_data, dict):
                if "pass" in check_data:
                    status = "✅" if check_data["pass"] else "⚠️"
                    value = check_data.get('value', check_data.get('value_mb', 'N/A'))
                    print(f"{status} {check_name}: {value}")
                    if not check_data.get("pass", True):
                        print(f"   要求: {check_data.get('requirement', 'N/A')}")
                    if "recommendation" in check_data:
                        print(f"   建议: {check_data['recommendation']}")
                else:
                    print(f"ℹ️  {check_name}: {check_data}")
            else:
                print(f"ℹ️  {check_name}: {check_data}")
    
    report_path = Path(paper_artifacts_dir) / "FIGURE_QUALITY_REPORT.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"✅ 报告已保存: {report_path}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    paper_artifacts_dir = project_root / "paper_artifacts"
    
    check_all_figures(paper_artifacts_dir)
