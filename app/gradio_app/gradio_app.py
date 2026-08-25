import gradio as gr

from app.ai.ai_clients.ollama_client import react_to_user_poor_swedish
from app.db import init_db
from app.i18n.service.translate_service import Language, Translator


def get_translations(lang: str) -> dict[str, str]:
    translator = Translator(lang)

    return {
        "input_label": translator.get("input_label"),
        "input_placeholder": translator.get("input_placeholder"),
        "correct_button": translator.get("correct_button"),
        "output_label": translator.get("output_label"),
        "output_placeholder": translator.get("output_placeholder"),
        "clear_button": translator.get("clear_button"),
    }


def update_translations(lang: str):
    translations = get_translations(lang)

    return (
        gr.Textbox(
            label=translations["input_label"],
            placeholder=translations["input_placeholder"],
        ),
        gr.Button(value=translations["correct_button"]),
        gr.Textbox(
            label=translations["output_label"],
            placeholder=translations["output_placeholder"],
        ),
        gr.Button(value=translations["clear_button"]),
    )


theme = gr.themes.Soft.from_hub("hmb/amethyst").set(
    input_background_fill_focus_dark="#13131F",
    input_background_fill_focus="#F4F2FF",
)

default_language = Language.Swedish.value
initial = get_translations(default_language)

with gr.Blocks(theme=theme) as tutor:
    gr.HTML(
        "<h2 style='text-align:center; font-size:2.2rem;'>"
        "Språkgranskaren"
        "</h2>"
    )

    language = gr.Dropdown(
        choices=[
            ("Polish", Language.Polish.value),
            ("Swedish", Language.Swedish.value),
            ("English", Language.English.value),
        ],
        value=default_language,
        label="Language:",
    )

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(
                label=initial["input_label"],
                placeholder=initial["input_placeholder"],
                lines=10,
            )

            with gr.Row(elem_classes="button-row"):
                correct_btn = gr.Button(
                    value=initial["correct_button"],
                    variant="primary",
                )

        with gr.Column():
            out = gr.Textbox(
                label=initial["output_label"],
                placeholder=initial["output_placeholder"],
                lines=10,
                interactive=False,
            )

            with gr.Row(elem_classes="button-row"):
                clear_btn = gr.Button(
                    value=initial["clear_button"],
                    variant="primary",
                )

    language.change(
        fn=update_translations,
        inputs=language,
        outputs=[user_input, correct_btn, out, clear_btn],
    )

    correct_btn.click(
        fn=react_to_user_poor_swedish,
        inputs=[user_input, language],
        outputs=out,
    )

    user_input.submit(
        fn=react_to_user_poor_swedish,
        inputs=[user_input, language],
        outputs=out,
    )

    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=[],
        outputs=[user_input, out],
    )


init_db()
tutor.launch(footer_links=[], share=True)