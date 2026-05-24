# Changelog

## [0.1.0] - 2025-05-24

### Added
- Initial release
- CLI command `inv-pdf [DIR] [-o OUTPUT] [-s SUFFIX] [-d DPI] [-j JOBS]`
- Python API: `invert_pdf(input_path, output_path, dpi=300)`
- Parallel processing via `ProcessPoolExecutor`
- Near-black pixel clamping (threshold=100) for clean dark output
- TOC and metadata preservation
- Dependencies: `pymupdf`, `Pillow`
