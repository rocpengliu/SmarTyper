def _on_mousewheel(canvas, event):
    if hasattr(canvas, 'yview_scroll'):
        if event.num == 5 or event.delta == -120:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            canvas.yview_scroll(-1, "units")
        elif hasattr(event, 'delta') and event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif hasattr(event, 'delta') and event.delta > 0:
            canvas.yview_scroll(-1, "units")