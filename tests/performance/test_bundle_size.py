#!/usr/bin/env python3
"""
Performance test for bundle size - Constitutional requirement: <500KB
Tests that frontend assets stay under 500KB total as per constitutional requirements.
"""

import os
import unittest
import gzip
from pathlib import Path


class BundleSizeTest(unittest.TestCase):
    """Test bundle sizes meet constitutional requirements (<500KB)"""

    def setUp(self):
        """Set up test parameters"""
        self.max_bundle_size = 500 * 1024  # Constitutional requirement: <500KB
        self.frontend_dir = Path("frontend")

        # Ensure frontend directory exists
        if not self.frontend_dir.exists():
            self.skipTest("Frontend directory not found - may not be implemented yet")

    def _get_file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

    def _get_gzipped_size(self, file_path):
        """Get gzipped file size (realistic network transfer size)"""
        try:
            with open(file_path, 'rb') as f:
                return len(gzip.compress(f.read()))
        except (OSError, IOError):
            return 0

    def test_css_bundle_size(self):
        """Test total CSS bundle size is under constitutional requirements"""
        css_dir = self.frontend_dir / "css"
        total_size = 0
        total_gzipped = 0
        css_files = []

        if css_dir.exists():
            for css_file in css_dir.glob("*.css"):
                file_size = self._get_file_size(css_file)
                gzipped_size = self._get_gzipped_size(css_file)
                total_size += file_size
                total_gzipped += gzipped_size
                css_files.append((css_file.name, file_size, gzipped_size))

        # Log individual file sizes for debugging
        for name, size, gzipped in css_files:
            print(f"CSS file {name}: {size} bytes ({gzipped} bytes gzipped)")

        print(f"Total CSS bundle: {total_size} bytes ({total_gzipped} bytes gzipped)")

        # Test raw size
        self.assertLess(total_size, self.max_bundle_size,
                       f"CSS bundle size {total_size} bytes exceeds constitutional requirement of {self.max_bundle_size} bytes")

        # Test gzipped size (more realistic)
        self.assertLess(total_gzipped, self.max_bundle_size // 2,
                       f"CSS bundle gzipped size {total_gzipped} bytes exceeds reasonable limit of {self.max_bundle_size // 2} bytes")

    def test_javascript_bundle_size(self):
        """Test total JavaScript bundle size is under constitutional requirements"""
        js_dir = self.frontend_dir / "js"
        total_size = 0
        total_gzipped = 0
        js_files = []

        if js_dir.exists():
            for js_file in js_dir.glob("*.js"):
                file_size = self._get_file_size(js_file)
                gzipped_size = self._get_gzipped_size(js_file)
                total_size += file_size
                total_gzipped += gzipped_size
                js_files.append((js_file.name, file_size, gzipped_size))

        # Log individual file sizes for debugging
        for name, size, gzipped in js_files:
            print(f"JS file {name}: {size} bytes ({gzipped} bytes gzipped)")

        print(f"Total JS bundle: {total_size} bytes ({total_gzipped} bytes gzipped)")

        # Test raw size
        self.assertLess(total_size, self.max_bundle_size,
                       f"JavaScript bundle size {total_size} bytes exceeds constitutional requirement of {self.max_bundle_size} bytes")

        # Test gzipped size (more realistic)
        self.assertLess(total_gzipped, self.max_bundle_size // 2,
                       f"JavaScript bundle gzipped size {total_gzipped} bytes exceeds reasonable limit of {self.max_bundle_size // 2} bytes")

    def test_html_pages_size(self):
        """Test HTML pages are reasonably sized"""
        pages_dir = self.frontend_dir / "pages"
        total_size = 0
        total_gzipped = 0
        html_files = []

        # Check both pages/ directory and root frontend for HTML files
        for search_dir in [pages_dir, self.frontend_dir]:
            if search_dir.exists():
                for html_file in search_dir.glob("*.html"):
                    file_size = self._get_file_size(html_file)
                    gzipped_size = self._get_gzipped_size(html_file)
                    total_size += file_size
                    total_gzipped += gzipped_size
                    html_files.append((html_file.name, file_size, gzipped_size))

        # Log individual file sizes for debugging
        for name, size, gzipped in html_files:
            print(f"HTML file {name}: {size} bytes ({gzipped} bytes gzipped)")

        print(f"Total HTML pages: {total_size} bytes ({total_gzipped} bytes gzipped)")

        # HTML should be much smaller than the full bundle limit
        html_limit = self.max_bundle_size // 4  # 125KB for all HTML

        self.assertLess(total_size, html_limit,
                       f"HTML pages total size {total_size} bytes exceeds reasonable limit of {html_limit} bytes")

    def test_total_frontend_bundle_size(self):
        """Test total frontend bundle (all assets) is under constitutional requirements"""
        total_size = 0
        total_gzipped = 0
        file_breakdown = {}

        # Scan all frontend files
        for file_path in self.frontend_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.html', '.css', '.js']:
                file_size = self._get_file_size(file_path)
                gzipped_size = self._get_gzipped_size(file_path)
                total_size += file_size
                total_gzipped += gzipped_size

                file_type = file_path.suffix
                if file_type not in file_breakdown:
                    file_breakdown[file_type] = {'size': 0, 'gzipped': 0, 'count': 0}

                file_breakdown[file_type]['size'] += file_size
                file_breakdown[file_type]['gzipped'] += gzipped_size
                file_breakdown[file_type]['count'] += 1

        # Log breakdown by file type
        print("\nFrontend bundle breakdown:")
        for file_type, stats in file_breakdown.items():
            print(f"{file_type}: {stats['count']} files, {stats['size']} bytes ({stats['gzipped']} bytes gzipped)")

        print(f"\nTotal frontend bundle: {total_size} bytes ({total_gzipped} bytes gzipped)")
        print(f"Constitutional requirement: <{self.max_bundle_size} bytes")

        # Test against constitutional requirement
        self.assertLess(total_size, self.max_bundle_size,
                       f"Total frontend bundle size {total_size} bytes exceeds constitutional requirement of {self.max_bundle_size} bytes")

        # Also test gzipped size (more realistic for network transfer)
        gzipped_limit = int(self.max_bundle_size * 0.7)  # Expect ~30% compression
        self.assertLess(total_gzipped, gzipped_limit,
                       f"Total frontend bundle gzipped size {total_gzipped} bytes exceeds reasonable limit of {gzipped_limit} bytes")

    def test_individual_large_files(self):
        """Test that no individual file is excessively large"""
        max_individual_file = self.max_bundle_size // 4  # No single file should be >125KB
        large_files = []

        for file_path in self.frontend_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.html', '.css', '.js']:
                file_size = self._get_file_size(file_path)

                if file_size > max_individual_file:
                    large_files.append((str(file_path), file_size))

        if large_files:
            large_files_msg = "\n".join([f"  {path}: {size} bytes" for path, size in large_files])
            self.fail(f"Individual files exceed reasonable size limit of {max_individual_file} bytes:\n{large_files_msg}")

    def test_chart_js_dependency_size(self):
        """Test Chart.js dependency size if included"""
        # Chart.js is the one allowed framework dependency
        # Check if it's included and verify its size is reasonable

        chart_js_files = []
        for file_path in self.frontend_dir.rglob("*chart*.js"):
            if file_path.is_file():
                file_size = self._get_file_size(file_path)
                chart_js_files.append((str(file_path), file_size))

        if chart_js_files:
            print("Chart.js files found:")
            total_chart_size = 0
            for path, size in chart_js_files:
                print(f"  {path}: {size} bytes")
                total_chart_size += size

            # Chart.js minified is ~60KB, allow up to 100KB for Chart.js files
            chart_js_limit = 100 * 1024
            self.assertLess(total_chart_size, chart_js_limit,
                           f"Chart.js dependency size {total_chart_size} bytes exceeds reasonable limit of {chart_js_limit} bytes")
        else:
            print("No Chart.js files found - may be loaded from CDN or not yet implemented")


if __name__ == "__main__":
    unittest.main()