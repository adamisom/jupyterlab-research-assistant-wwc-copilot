#!/usr/bin/env python3
"""Verify package configuration for release readiness."""

import json
import sys
from pathlib import Path

def check_package_json():
    """Check package.json configuration."""
    print("=" * 60)
    print("Checking package.json")
    print("=" * 60)
    
    with open("package.json") as f:
        pkg = json.load(f)
    
    issues = []
    checks = []
    
    # Version
    version = pkg.get("version")
    if version:
        checks.append(f"✓ Version: {version}")
        if version == "0.0.0":
            issues.append("⚠ Version is 0.0.0 - should be updated for release")
    else:
        issues.append("✗ Missing version")
    
    # Description
    desc = pkg.get("description")
    if desc and len(desc) > 10:
        checks.append(f"✓ Description: {desc[:50]}...")
    else:
        issues.append("✗ Missing or too short description")
    
    # Author
    author = pkg.get("author")
    if author:
        if isinstance(author, dict):
            name = author.get("name", "")
            email = author.get("email", "")
            if name and email:
                checks.append(f"✓ Author: {name} <{email}>")
            else:
                issues.append("✗ Author missing name or email")
        else:
            checks.append(f"✓ Author: {author}")
    else:
        issues.append("✗ Missing author")
    
    # Keywords
    keywords = pkg.get("keywords", [])
    if keywords and len(keywords) >= 3:
        checks.append(f"✓ Keywords: {', '.join(keywords)}")
    else:
        issues.append("⚠ Keywords: Should have at least 3 keywords")
    
    # URLs for hatch-nodejs-version
    homepage = pkg.get("homepage")
    repository = pkg.get("repository", {})
    bugs = pkg.get("bugs", {})
    
    if homepage:
        checks.append(f"✓ Homepage: {homepage}")
    else:
        issues.append("⚠ Missing homepage (used for PyPI URLs)")
    
    if repository.get("url"):
        checks.append(f"✓ Repository: {repository['url']}")
    else:
        issues.append("⚠ Missing repository URL (used for PyPI URLs)")
    
    if bugs.get("url"):
        checks.append(f"✓ Bug Tracker: {bugs['url']}")
    else:
        issues.append("⚠ Missing bugs URL (used for PyPI URLs)")
    
    # License
    license_field = pkg.get("license")
    if license_field:
        checks.append(f"✓ License: {license_field}")
    else:
        issues.append("✗ Missing license")
    
    print("\n".join(checks))
    if issues:
        print("\nIssues found:")
        print("\n".join(issues))
    else:
        print("\n✓ All package.json checks passed!")
    
    return len([i for i in issues if i.startswith("✗")]) == 0

def check_pyproject_toml():
    """Check pyproject.toml configuration."""
    print("\n" + "=" * 60)
    print("Checking pyproject.toml")
    print("=" * 60)
    
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("⚠ Cannot parse TOML (tomli/tomllib not available)")
            print("  Install with: pip install tomli")
            return True
    
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    issues = []
    checks = []
    
    project = config.get("project", {})
    
    # Name
    name = project.get("name")
    if name:
        checks.append(f"✓ Package name: {name}")
    else:
        issues.append("✗ Missing project name")
    
    # Readme
    readme = project.get("readme")
    if readme:
        checks.append(f"✓ Readme: {readme}")
        if not Path(readme).exists():
            issues.append(f"✗ Readme file not found: {readme}")
    else:
        issues.append("⚠ Missing readme field")
    
    # License
    license_config = project.get("license")
    if license_config:
        if isinstance(license_config, dict) and "file" in license_config:
            license_file = license_config["file"]
            checks.append(f"✓ License file: {license_file}")
            if not Path(license_file).exists():
                issues.append(f"✗ License file not found: {license_file}")
        else:
            checks.append(f"✓ License: {license_config}")
    else:
        issues.append("✗ Missing license configuration")
    
    # Dynamic fields
    dynamic = project.get("dynamic", [])
    if "version" in dynamic:
        checks.append("✓ Version is dynamic (will sync from package.json)")
    if "description" in dynamic:
        checks.append("✓ Description is dynamic (will sync from package.json)")
    if "authors" in dynamic:
        checks.append("✓ Authors is dynamic (will sync from package.json)")
    if "urls" in dynamic:
        checks.append("✓ URLs is dynamic (will sync from package.json)")
    if "keywords" in dynamic:
        checks.append("✓ Keywords is dynamic (will sync from package.json)")
    
    # Dependencies
    deps = project.get("dependencies", [])
    if deps:
        checks.append(f"✓ Dependencies: {len(deps)} packages listed")
    else:
        issues.append("⚠ No dependencies listed")
    
    # Classifiers
    classifiers = project.get("classifiers", [])
    if classifiers:
        checks.append(f"✓ Classifiers: {len(classifiers)} classifiers")
    else:
        issues.append("⚠ No classifiers (helps with PyPI discoverability)")
    
    print("\n".join(checks))
    if issues:
        print("\nIssues found:")
        print("\n".join(issues))
    else:
        print("\n✓ All pyproject.toml checks passed!")
    
    return len([i for i in issues if i.startswith("✗")]) == 0

def check_install_json():
    """Check install.json."""
    print("\n" + "=" * 60)
    print("Checking install.json")
    print("=" * 60)
    
    if not Path("install.json").exists():
        print("✗ install.json not found!")
        return False
    
    with open("install.json") as f:
        install = json.load(f)
    
    checks = []
    issues = []
    
    if install.get("packageManager") == "python":
        checks.append("✓ packageManager: python")
    else:
        issues.append("⚠ packageManager should be 'python'")
    
    if install.get("packageName"):
        checks.append(f"✓ packageName: {install['packageName']}")
    else:
        issues.append("✗ Missing packageName")
    
    if install.get("uninstallInstructions"):
        checks.append("✓ uninstallInstructions present")
    else:
        issues.append("⚠ Missing uninstallInstructions")
    
    print("\n".join(checks))
    if issues:
        print("\nIssues found:")
        print("\n".join(issues))
    
    return len([i for i in issues if i.startswith("✗")]) == 0

def check_license():
    """Check LICENSE file."""
    print("\n" + "=" * 60)
    print("Checking LICENSE file")
    print("=" * 60)
    
    license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
    found = None
    
    for lic_file in license_files:
        if Path(lic_file).exists():
            found = lic_file
            break
    
    if found:
        print(f"✓ License file found: {found}")
        # Check if it's not empty
        size = Path(found).stat().st_size
        if size > 100:
            print(f"✓ License file has content ({size} bytes)")
            return True
        else:
            print("⚠ License file seems too small")
            return False
    else:
        print("✗ No LICENSE file found!")
        print("  Expected one of: " + ", ".join(license_files))
        return False

def main():
    """Run all checks."""
    print("Package Configuration Verification")
    print("=" * 60)
    print()
    
    results = []
    results.append(("package.json", check_package_json()))
    results.append(("pyproject.toml", check_pyproject_toml()))
    results.append(("install.json", check_install_json()))
    results.append(("LICENSE", check_license()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All package configuration checks passed!")
        print("  Ready for release!")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

