import os
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from queue import Queue
from types import SimpleNamespace
from unittest.mock import Mock, patch

import customtkinter as ctk
import matplotlib.pyplot as plt
import pymupdf

from scripts.class_modules.microhap_class import MicroHapClass
from scripts.genotype.results_reads_all import load_pdf_from_here
from scripts.genotype.results_viewer import create_reads_panel


class AllReadsDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.microhap = MicroHapClass()
        self.microhap.set_assigned_sam_reads_dict(
            {f"sample_{i}": 1000 - i for i in range(41)}
        )
        self.path = Path(self.temp.name) / "All_sample_read_distribution.pdf"
        self.genoclass = SimpleNamespace(
            get_parameter=lambda: SimpleNamespace(get_outputdir=lambda: self.temp.name),
            get_microhap=lambda: self.microhap,
        )

    def test_generates_ordered_pdf_pages(self):
        messages = Queue()
        self.microhap.pro_all_sample_read_distri_fig_pdf(self.temp.name, messages, n_threads=2)
        with pymupdf.open(self.path) as doc:
            self.assertEqual(len(doc), 2)
            self.assertIn("sample_0", doc[0].get_text())
            self.assertNotIn("sample_40", doc[0].get_text())
            self.assertIn("sample_40", doc[1].get_text())
            for page in doc:
                self.assertIn("Reads distribution of all samples", page.get_text())
                self.assertGreater(len(page.get_pixmap().samples), 0)
        self.assertIn("finished", messages.get_nowait() + messages.get_nowait())

    def test_empty_data_is_reported_without_creating_pdf(self):
        self.microhap.set_assigned_sam_reads_dict({})
        with self.assertRaisesRegex(ValueError, "No assigned sample reads"):
            self.microhap.pro_all_sample_read_distri_fig_pdf(self.temp.name, Queue())
        self.assertFalse(self.path.exists())

    def test_page_failure_is_not_reported_as_success(self):
        messages = Queue()
        with patch(
            "scripts.class_modules.microhap_class.generate_page",
            side_effect=RuntimeError("plot failed"),
        ):
            with self.assertRaisesRegex(RuntimeError, "plot failed"):
                self.microhap.pro_all_sample_read_distri_fig_pdf(self.temp.name, messages)
        self.assertEqual(messages.qsize(), 1)

    def test_missing_distribution_is_generated_and_loaded(self):
        canvas = Mock()
        with patch("scripts.genotype.results_reads_all.load_pdf") as load:
            load_pdf_from_here(self.genoclass, canvas, "distri")
        self.assertTrue(self.path.is_file())
        load.assert_called_once_with(str(self.path), canvas)

    def test_existing_distribution_is_loaded_without_regeneration(self):
        self.microhap.pro_all_sample_read_distri_fig_pdf(self.temp.name, Queue())
        with patch.object(self.microhap, "pro_all_sample_read_distri_fig_pdf") as generate:
            with patch("scripts.genotype.results_reads_all.load_pdf") as load:
                canvas = Mock()
                load_pdf_from_here(self.genoclass, canvas, "distri")
        generate.assert_not_called()
        load.assert_called_once_with(str(self.path), canvas)

    def test_missing_read_data_shows_error(self):
        self.microhap.set_assigned_sam_reads_dict({})
        with patch("scripts.genotype.results_reads_all.showerror") as error:
            with patch("scripts.genotype.results_reads_all.load_pdf") as load:
                load_pdf_from_here(self.genoclass, Mock(), "distri")
        error.assert_called_once()
        self.assertIn("No assigned sample reads", error.call_args.args[2])
        load.assert_not_called()

    @unittest.skipUnless(os.environ.get("DISPLAY"), "Requires a graphical display")
    def test_pdf_pages_are_displayed_on_canvas(self):
        root = tk.Tk()
        try:
            canvas = tk.Canvas(root)
            canvas.pack()
            with patch("scripts.genotype.results_reads_all.showerror") as error:
                load_pdf_from_here(self.genoclass, canvas, "distri")
                root.update_idletasks()
            error.assert_not_called()
            self.assertEqual(len(canvas.image_refs), 2)
            self.assertEqual(len(canvas.find_all()), 2)
            self.assertIsNotNone(canvas.bbox("all"))
        finally:
            root.destroy()
            plt.close("all")

    @unittest.skipUnless(os.environ.get("DISPLAY"), "Requires a graphical display")
    def test_all_sample_distribution_button_loads_pdf(self):
        with pymupdf.open() as doc:
            doc.new_page().insert_text((50, 50), "Read quality")
            doc.save(Path(self.temp.name) / "All_sample_read_quality.pdf")
        root = tk.Tk()
        try:
            top_panel = ctk.CTkFrame(root)
            top_panel.button_child_refs = {}
            parent = SimpleNamespace(master=SimpleNamespace(
                genotype_class=self.genoclass,
                pages={"results": SimpleNamespace(body_frame=SimpleNamespace(top_panel=top_panel))},
            ))
            bottom_panel = ctk.CTkFrame(root)
            with patch("scripts.genotype.results_reads_all.showerror") as error:
                create_reads_panel(parent, bottom_panel, "all")
                self.assertFalse(self.path.exists())
                top_panel.button_child_refs["a_distribution"].invoke()
                root.update_idletasks()
            error.assert_not_called()
            figure_panel = bottom_panel.grid_slaves(row=1, column=0)[0]
            container = figure_panel.grid_slaves(row=0, column=0)[0]
            canvas = container.grid_slaves(row=0, column=0)[0]
            self.assertEqual(len(canvas.image_refs), 2)
            self.assertEqual(len(canvas.find_all()), 2)
        finally:
            root.destroy()
            plt.close("all")
