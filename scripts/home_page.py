import customtkinter as ctk
from .utils.colors import COLORS
from .utils.common import title_font, subtitle_font, card_title_font, card_desc_font
from .utils.smartyper_logo import SmarTyperLogo

def create_home(parent, app):
    # Modern fonts
    page = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(0, weight=3)  # Header row will expand more
    page.grid_rowconfigure(1, weight=1)  # Content row will expand less (shorter)
    page.grid_rowconfigure(2, weight=1)  # Footer row

    home_title_font = ctk.CTkFont(family="Segoe UI", size=64, weight="bold", slant="italic")
    home_subtitle_font = ctk.CTkFont(family="Segoe UI", size=18)
    home_card_title_font = ctk.CTkFont(family="Segoe UI", size=34, weight="bold")
    home_card_desc_font = ctk.CTkFont(family="Segoe UI", size=14)
    home_button_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
    home_footer_font = ctk.CTkFont(family="Segoe UI", size=10)

    # Modern Header Frame with gradient-like effect (AI style)

    header_frame = ctk.CTkFrame(page, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0))
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_rowconfigure(0, weight=1)
    header_frame.grid_rowconfigure(1, weight=0)

    # Composite label for colored S and T in SmarTyper
    header_label_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    header_label_frame.grid(row=0, column=0, pady=(18, 10), sticky="nsew")
    header_label_frame.grid_columnconfigure(0, weight=1)
    header_label_frame.grid_columnconfigure(1, weight=0)
    header_label_frame.grid_columnconfigure(2, weight=1)
    # Use an internal frame to center the label group in column 1
    label_inner = ctk.CTkFrame(header_label_frame, fg_color="transparent")
    label_inner.grid(row=0, column=1)
    welcome_label = ctk.CTkLabel(
        label_inner,
        text="Welcome to ",
        font=home_title_font,
        fg_color="transparent",
        text_color=COLORS['home']
    )
    welcome_label.pack(side="left")
    s_label = ctk.CTkLabel(
        label_inner,
        text="S",
        font=home_title_font,
        fg_color="transparent",
        text_color=COLORS['success']
    )
    s_label.pack(side="left")
    mar_label = ctk.CTkLabel(
        label_inner,
        text="mar",
        font=home_title_font,
        fg_color="transparent",
        text_color=COLORS['home']
    )
    mar_label.pack(side="left")
    t_label = ctk.CTkLabel(
        label_inner,
        text="T",
        font=home_title_font,
        fg_color="transparent",
        text_color=COLORS['primary']
    )
    t_label.pack(side="left")
    yper_label = ctk.CTkLabel(
        label_inner,
        text="yper",
        font=home_title_font,
        fg_color="transparent",
        text_color=COLORS['home']
    )
    yper_label.pack(side="left")

    header_label2 = ctk.CTkLabel(
        header_frame,
        text="-- A smart, reference-free & unified platform for microhaplotype and micropeptype genotyping, visualization from amplicon sequence data",
        font=home_subtitle_font,
        fg_color="transparent",
        text_color=COLORS['text_secondary'],
        justify="center"
    )
    header_label2.grid(row=1, column=0, pady=(0, 10))

    # Main panel for the four cards
    grid_padx = 40
    main_panel = ctk.CTkFrame(page, fg_color="transparent")
    main_panel.grid(row=1, column=0, sticky="nsew", padx=grid_padx, pady=(0, 5))
    for i in range(2):
        main_panel.grid_columnconfigure(i, weight=1, uniform="card")
        main_panel.grid_rowconfigure(i, weight=1, uniform="card")
    cards = [
        {"title": "Genotyping", "desc": "\u2022Read raw amplicon sequence data (fastq.gz)\n\u2022Conduct read quality control\n\u2022Demultiplex reads based on locus's primer sequences\n\u2022Extract various features\n\u2022Predict zygosity & genotype\n\u2022Review & correct genotype on interactive genotype plot\n\u2022Based on software tool Seq2Type", "color": COLORS['primary'], "row": 0, "col": 0, "page": "genotyping"},
        {"title": "Microtyping", "desc": "\u2022Identify & visualize microtypes (microhaplotype & micropeptype)\n\u2022Align sequence & construct phylogenetic tree\n\u2022Visualize microtype & sequence alignment\n\u2022Visualize phylogenetic tree\n\u2022Generate microtype plot\n\u2022Based on output genotype file from Genotype module\n", "color": COLORS['accent'], "row": 0, "col": 1, "page": "microtyping"},
        {"title": "Machine Learning", "desc": "\u2022Train ML models\n\u2022Apply models to feature table\n\u2022Predict zygosity & genotype for smart genotyping\n\u2022Based on an existing genotype table\n\u2022This module is optional", "color": COLORS['success'], "row": 1, "col": 0, "page": "machine learning"},
        {"title": "Project Management", "desc": "\u2022Manage existing projects\n\u2022Review & reedit genotype\n\u2022Review microtype\n\n", "color": COLORS['workflow_gold'], "row": 1, "col": 1, "page": "project"}
    ]
    bullet_labels = []
    card_title_labels = []
    card_buttons = []

    def create_modern_card(parent, card_data, app):
        # Card with border color matching its main color
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=14, border_width=2, border_color=card_data["color"])
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        # Card content
        content_area = ctk.CTkFrame(card, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=25, pady=(20, 10))
        title = ctk.CTkLabel(content_area, text=card_data["title"], font=home_card_title_font, text_color=card_data["color"])
        title.pack(pady=(10, 8), fill="x")
        card_title_labels.append(title)
        # Display each bullet as a separate label (one line per bullet)
        for line in card_data["desc"].split("\n"):
            bullet_label = ctk.CTkLabel(
                content_area,
                text=line,
                font=home_card_desc_font,
                text_color=COLORS['text_secondary'],
                justify="left",
                anchor="w"
            )
            bullet_label.pack(anchor="w", padx=130, fill="x")
            bullet_labels.append(bullet_label)
        btn = ctk.CTkButton(
            content_area,
            text="Open →",
            fg_color=card_data["color"],
            hover_color="#7F5CFF",
            corner_radius=10,
            height=45,
            font=home_button_font,
            command=lambda: app.show_page(card_data["page"])
        )
        btn.pack(pady=(10, 15), padx=20, fill="x")
        card_buttons.append(btn)
        return card

    for card in cards:
        card_frame = create_modern_card(main_panel, card, app)
        card_frame.grid(row=card["row"], column=card["col"], padx=15, pady=15, sticky="nsew")

    # Two horizontal panels for contact and citation, aligned side by side
    lower_panel = ctk.CTkFrame(page, fg_color="transparent", corner_radius=12)
    lower_panel.grid(row=2, column=0, sticky="ew", padx=40, pady=(2, 15))
    lower_panel.grid_columnconfigure(0, weight=1)
    lower_panel.grid_columnconfigure(1, weight=1)
    lower_panel.grid_rowconfigure(0, weight=1)

    contact_name = "Contact: Dr. Peng Liu"
    contact_email = "peng.liu@ec.gc.ca"
    contact_org = "Environment and Climate Change Canada"
    citation_text = "Citation: Liu, P. et al. SmarTyper: a reference-free and unified platform for microhaplotype and micropeptype genotyping. (2026)."
    github_text = "Github: https://github.com/rocpengliu/SmarTyper"

    contact_panel = ctk.CTkFrame(lower_panel, fg_color="transparent")
    contact_panel.grid(row=0, column=0, sticky="ne", padx=(0, 10))
    contact_panel.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        contact_panel,
        text=contact_name,
        font=home_footer_font,
        text_color=COLORS['text_secondary'],
        fg_color="transparent",
        height=14,
        anchor="e",
        justify="right"
    ).grid(row=0, column=0, sticky="e", pady=0)

    email_label = ctk.CTkLabel(
        contact_panel,
        text=f"Email: {contact_email}",
        font=home_footer_font,
        text_color=COLORS['text_secondary'],
        fg_color="transparent",
        height=14,
        anchor="e",
        justify="right"
    )
    email_label.grid(row=1, column=0, sticky="e", pady=0)

    ctk.CTkLabel(
        contact_panel,
        text=contact_org,
        font=home_footer_font,
        text_color=COLORS['text_secondary'],
        fg_color="transparent",
        height=14,
        anchor="e",
        justify="right"
    ).grid(row=2, column=0, sticky="e", pady=0)

    citation_panel = ctk.CTkFrame(lower_panel, fg_color="transparent")
    citation_panel.grid(row=0, column=1, sticky="nw", padx=(10, 0))
    citation_panel.grid_columnconfigure(0, weight=1)

    citation_label = ctk.CTkLabel(
        citation_panel,
        text=citation_text,
        font=home_footer_font,
        text_color=COLORS['text_secondary'],
        fg_color="transparent",
        height=14,
        anchor="w",
        justify="left"
    )
    citation_label.grid(row=0, column=0, sticky="w", pady=0)

    github_label = ctk.CTkLabel(
        citation_panel,
        text=github_text,
        font=home_footer_font,
        text_color=COLORS['text_secondary'],
        fg_color="transparent",
        height=14,
        anchor="w",
        justify="left"
    )
    github_label.grid(row=1, column=0, sticky="w", pady=0)

    last_width_bucket = {"value": None}

    def apply_responsive_layout(width):
        if width >= 1700:
            scale = 1.0
        elif width >= 1450:
            scale = 0.9
        elif width >= 1280:
            scale = 0.8
        elif width >= 1100:
            scale = 0.72
        elif width >= 900:
            scale = 0.62
        else:
            scale = 0.54

        bucket = scale
        if last_width_bucket["value"] == bucket:
            return
        last_width_bucket["value"] = bucket

        horizontal_pad = max(12, int(40 * scale))
        header_top_pad = max(8, int(20 * scale))
        header_inner_pad_top = max(6, int(18 * scale))
        header_inner_pad_bottom = max(4, int(10 * scale))
        bullet_padx = max(14, min(80, width // 20))

        home_title_font.configure(size=max(34, int(64 * scale)))
        home_subtitle_font.configure(size=max(12, int(18 * scale)))
        home_card_title_font.configure(size=max(28, int(34 * scale)))
        home_card_desc_font.configure(size=max(12, int(14 * scale)))
        home_button_font.configure(size=max(11, int(14 * scale)))
        home_footer_font.configure(size=max(8, int(10 * scale)))

        header_frame.grid_configure(pady=(header_top_pad, 0))
        header_label_frame.grid_configure(pady=(header_inner_pad_top, header_inner_pad_bottom))
        main_panel.grid_configure(padx=horizontal_pad)
        lower_panel.grid_configure(padx=horizontal_pad)

        content_width = max(520, width - 260)
        header_label2.configure(wraplength=max(460, content_width - 80))
        citation_wrap = max(180, (content_width // 2) - 30)
        citation_label.configure(wraplength=citation_wrap)
        github_label.configure(wraplength=citation_wrap)

        if width < 1150:
            lower_panel.grid_columnconfigure(0, weight=1)
            lower_panel.grid_columnconfigure(1, weight=0)
            contact_panel.grid_configure(row=0, column=0, sticky="w", padx=0, pady=(0, 4))
            citation_panel.grid_configure(row=1, column=0, sticky="w", padx=0, pady=0)
        else:
            lower_panel.grid_columnconfigure(0, weight=1)
            lower_panel.grid_columnconfigure(1, weight=1)
            contact_panel.grid_configure(row=0, column=0, sticky="ne", padx=(0, 10), pady=0)
            citation_panel.grid_configure(row=0, column=1, sticky="nw", padx=(10, 0), pady=0)

        bullet_wrap = max(140, (content_width // 2) - 220)
        for label in bullet_labels:
            label.pack_configure(padx=bullet_padx)
            label.configure(wraplength=bullet_wrap)

        button_height = max(32, int(45 * scale))
        for button in card_buttons:
            button.configure(height=button_height)

    def on_page_configure(event):
        if event.widget is page:
            apply_responsive_layout(event.width)

    page.bind("<Configure>", on_page_configure)
    page.after(50, lambda: apply_responsive_layout(page.winfo_width()))

    return page

