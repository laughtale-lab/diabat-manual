import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1] / 'tools' / 'audit-mdbook.py'
spec=importlib.util.spec_from_file_location('auditbook',SCRIPT)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class AuditTest(unittest.TestCase):
    def test_source_links_and_anchors(self):
        with tempfile.TemporaryDirectory() as d:
            book=Path(d);src=book/'src';src.mkdir()
            (src/'SUMMARY.md').write_text('[Welcome](README.md)\n',encoding='utf8')
            (src/'README.md').write_text('<a id="start"></a>\n[Intro](introduction.md#intro)\n<a href="diabat.pdf">PDF</a>',encoding='utf8')
            (src/'introduction.md').write_text('<a id="intro"></a>\nhello',encoding='utf8')
            for name in ['references.md','example-inputs.md','diabatization.md']:
                (src/name).write_text('ok',encoding='utf8')
            (src/'diabat.css').write_text('ok',encoding='utf8')
            (src/'diabat-highlight.js').write_text('ok',encoding='utf8')
            for n in range(10): (src/f'extra-{n}.md').write_text('ok',encoding='utf8')
            stats={'pages':15,'resolved_links':200, 'keywords':1,'overview_items':1,
                   'script_labels':1,'example_labels':1,'original_input_files':1,'references_used':1}
            (book/'conversion-report.json').write_text(json.dumps({'statistics':stats,'labels':{'intro':{'page':'introduction.md'}}}),encoding='utf8')
            audit.audit_sources(book, book/'conversion-report.json')
            (src/'introduction.md').write_text('<a id="wrong"></a>\nhello',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'anchor'):
                audit.audit_sources(book, book/'conversion-report.json')
            (src/'introduction.md').write_text('<a id="intro"></a> L"owdin', encoding='utf8')
            with self.assertRaisesRegex(ValueError,'diaeresis'):
                audit.audit_sources(book, book/'conversion-report.json')

    def test_relative_site_root_and_actionable_link_errors(self):
        # GitHub Actions invokes: audit-mdbook.py site site main.pdf.
        # Previously, missing links/anchors raised a misleading
        # "absolute path is not in the subpath of 'site'" exception.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            site = root / 'site'
            site.mkdir()
            (root / 'original.pdf').write_bytes(b'pdf')
            (site / 'diabat.pdf').write_bytes(b'pdf')
            for name in ['diabat.css', 'diabat-highlight.js', 'searchindex.js']:
                (site / name).write_text('ok', encoding='utf8')
            (site / 'index.html').write_text(
                '<a href="diabatization.html#target">Go</a>', encoding='utf8'
            )
            (site / 'diabatization.html').write_text(
                '<a id="target"></a>', encoding='utf8'
            )
            (site / 'references.html').write_text('<h1>Refs</h1>', encoding='utf8')
            (site / 'build-info.json').write_text(
                json.dumps({'site_mode': 'mdbook'}), encoding='utf8'
            )

            def run_audit():
                return subprocess.run(
                    [sys.executable, str(SCRIPT), 'site', 'site', 'original.pdf'],
                    cwd=root, capture_output=True, text=True
                )

            result = run_audit()
            self.assertEqual(result.returncode, 0, result.stderr)

            (site / 'diabatization.html').write_text(
                '<a id="other"></a>', encoding='utf8'
            )
            result = run_audit()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Missing published HTML anchor:', result.stderr)
            self.assertIn('index.html -> diabatization.html#target', result.stderr)
            self.assertNotIn('is not in the subpath', result.stderr)

            (site / 'index.html').write_text(
                '<a href="missing.html">Broken</a>', encoding='utf8'
            )
            result = run_audit()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Missing deployed link or resource:', result.stderr)
            self.assertIn('index.html -> missing.html', result.stderr)
            self.assertNotIn('is not in the subpath', result.stderr)

    def test_html_site_and_pdf_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            site=Path(d);pdf=site/'original.pdf';pdf.write_bytes(b'pdf')
            (site/'diabat.pdf').write_bytes(b'pdf')
            for name in ['diabat.css','diabat-highlight.js','searchindex.js']:
                (site/name).write_text('ok',encoding='utf8')
            (site/'index.html').write_text('<a href="diabatization.html#target">Go</a><a href="diabat.pdf">PDF</a>',encoding='utf8')
            (site/'diabatization.html').write_text('<a id="target"></a>',encoding='utf8')
            (site/'references.html').write_text('<h1>Refs</h1>',encoding='utf8')
            (site/'build-info.json').write_text(json.dumps({'site_mode':'mdbook'}),encoding='utf8')
            audit.audit_site(site,pdf)
            (site/'diabatization.html').write_text('<h1>Bad</h1>',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'anchor'):
                audit.audit_site(site,pdf)
            (site/'diabat.pdf').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'PDF'):
                audit.audit_site(site,pdf)

if __name__=='__main__': unittest.main()
