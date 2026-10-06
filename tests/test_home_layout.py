import os
import unittest

import customtkinter as ctk

from smartyper import SmarTyperApp


@unittest.skipUnless(os.environ.get("DISPLAY"), "Requires a graphical display")
class HomeLayoutTests(unittest.TestCase):
    def test_sidebar_visibility_survives_scaling(self):
        root = SmarTyperApp()
        try:
            root.after(800, root.quit)
            root.mainloop()
            self.assertFalse(any(root.menu_expanded.values()))
            self._assert_visible_menus(root, set())
            self.assertTrue(root.pages["home"].winfo_ismapped())
            for name, page in root.pages.items():
                if name != "home":
                    self.assertFalse(page.winfo_ismapped(), name)

            for scale in (0.7, 0.9):
                ctk.set_widget_scaling(scale)
                root.update_idletasks()
                self._assert_visible_menus(root, set())

            root.show_page("genotyping")
            root.update_idletasks()
            self._assert_visible_menus(root, {"genotyping"})
            rows = [button.grid_info()["row"] for button in root.children_button_refs["genotyping"]]
            ctk.set_widget_scaling(0.8)
            root.update_idletasks()
            self._assert_visible_menus(root, {"genotyping"})
            self.assertEqual(
                rows,
                [button.grid_info()["row"] for button in root.children_button_refs["genotyping"]],
            )

            root.show_page("microtyping")
            ctk.set_widget_scaling(0.6)
            root.update_idletasks()
            self._assert_visible_menus(root, {"microtyping"})

            root.show_page("microtyping")
            ctk.set_widget_scaling(0.75)
            root.update_idletasks()
            self._assert_visible_menus(root, set())

            root.show_page("genotyping")
            root.show_page("home")
            ctk.set_widget_scaling(0.85)
            root.update_idletasks()
            self._assert_visible_menus(root, set())
        finally:
            root.destroy()
            ctk.set_widget_scaling(1.0)

    def _assert_visible_menus(self, root, expected):
        for menu, buttons in root.children_button_refs.items():
            self.assertEqual(root.menu_expanded[menu], menu in expected)
            for button in buttons:
                self.assertEqual(bool(button.winfo_ismapped()), menu in expected, menu)

    def test_header_footer_and_card_buttons_fit(self):
        root = SmarTyperApp()
        try:
            page = root.pages["home"]
            root.after(800, root.quit)
            root.mainloop()
            scales = []
            for width, height in ((1908, 1047), (1468, 800), (1280, 752), (1024, 640), (1908, 1047)):
                with self.subTest(width=width, height=height):
                    root.attributes("-zoomed", False)
                    root.update()
                    root.geometry(f"{width}x{height}+30+30")
                    root.after(1800, root.quit)
                    root.mainloop()
                    scales.append(root._interface_scale)
                    header = next(
                        child for child in page.winfo_children()
                        if child.grid_info().get("row") == 0
                    )
                    footer = next(
                        child for child in page.winfo_children()
                        if child.grid_info().get("row") == 2
                    )
                    self.assertGreaterEqual(header.winfo_height(), header.winfo_reqheight())
                    self.assertGreaterEqual(footer.winfo_height(), footer.winfo_reqheight())
                    self.assertLessEqual(footer.winfo_y() + footer.winfo_height(), page.winfo_height())
                    self.assertFalse(any(
                        isinstance(child, ctk.CTkScrollableFrame)
                        for child in self._descendants(page)
                    ))
                    card_panel = next(
                        child for child in self._descendants(page)
                        if child.master is page and child.grid_info().get("row") == 1
                    )
                    labels = [
                        child for child in self._descendants(header)
                        if isinstance(child, ctk.CTkLabel) and child.cget("text") == "Welcome to "
                    ]
                    self.assertEqual(len(labels), 1)
                    label = labels[0]
                    for ancestor in (label.master, label.master.master, header):
                        self.assertGreaterEqual(
                            ancestor.winfo_rooty() + ancestor.winfo_height(),
                            label.winfo_rooty() + label.winfo_height(),
                        )
                    buttons = [
                        child for child in self._descendants(card_panel)
                        if isinstance(child, ctk.CTkButton)
                    ]
                    self.assertEqual(len(buttons), 4)
                    for button in buttons:
                        self.assertTrue(button.winfo_ismapped())
                        self.assertGreaterEqual(button.winfo_height(), int(45 * root._interface_scale) - 1)
                    for child in self._descendants(page):
                        if not isinstance(child, (ctk.CTkLabel, ctk.CTkButton)):
                            continue
                        if isinstance(child, ctk.CTkLabel):
                            self.assertGreaterEqual(
                                child._label.winfo_width(), child._label.winfo_reqwidth()
                            )
                            self.assertGreaterEqual(
                                child._label.winfo_height(), child._label.winfo_reqheight()
                            )
                        self.assertGreaterEqual(child.winfo_rooty(), page.winfo_rooty())
                        self.assertLessEqual(
                            child.winfo_rooty() + child.winfo_height(),
                            page.winfo_rooty() + page.winfo_height(),
                        )
                        self.assertGreaterEqual(child.winfo_rootx(), page.winfo_rootx())
                        self.assertLessEqual(
                            child.winfo_rootx() + child.winfo_width(),
                            page.winfo_rootx() + page.winfo_width(),
                        )
                    self.assertLessEqual(
                        root.exit_button.winfo_rooty() + root.exit_button.winfo_height(),
                        root.winfo_rooty() + root.winfo_height(),
                    )
            self.assertGreater(scales[0], scales[3])
            self.assertAlmostEqual(scales[0], scales[4], places=2)
        finally:
            root.destroy()
            ctk.set_widget_scaling(1.0)

    @staticmethod
    def _descendants(widget):
        for child in widget.winfo_children():
            yield child
            yield from HomeLayoutTests._descendants(child)
