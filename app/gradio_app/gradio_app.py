import gradio as gr

from app.ai.ai_clients.ollama_client import react_to_user_poor_swedish

theme = gr.themes.Soft.from_hub("hmb/amethyst")

with gr.Blocks(theme=theme) as tutor:
    with gr.Row():
        gr.Markdown("# Språkgranskaren")

    with gr.Row():

        user_input = gr.Textbox(
            label="Enter your broken Swedish here:",
            placeholder="Skriv din bristfälliga svenska.",
            lines=10,
            scale=5
        )
        with gr.Row(elem_classes="button-row"):
            correct_btn = gr.Button("Correct me!", variant="primary")

        out = gr.Textbox(
            lines=10,
            label="Korrigerat svenskt",
            placeholder="...AI output will appear here",
            scale=5,
            interactive=False
        )
    correct_btn.click(
        react_to_user_poor_swedish,
        inputs=user_input,
        outputs=out
    )

    user_input.submit(
        react_to_user_poor_swedish,
        inputs=user_input,
        outputs=out
    )


tutor.launch(share=True)


