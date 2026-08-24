import gradio as gr

from app.ai.ai_clients.ollama_client import react_to_user_poor_swedish

theme = gr.themes.Soft.from_hub("hmb/amethyst").set(
    input_background_fill_focus_dark="#13131F",
    input_background_fill_focus="#F4F2FF",
)

with gr.Blocks(
        theme=theme

) as tutor:
    gr.HTML("<h2 style='text-align:center; font-size:2.2rem;'>Språkgranskaren</h2>")

    with gr.Row():

        with gr.Column():
            user_input = gr.Textbox(
                label="Enter your broken Swedish here:",
                placeholder="Skriv din bristfälliga svenska.",
                lines=10,
            )
            with gr.Row(elem_classes="button-row"):
                correct_btn = gr.Button("Correct me!", variant="primary")
        with gr.Column():
            out = gr.Textbox(
                lines=10,
                label="Korrigerat svenskt",
                placeholder="...AI output will appear here",
                interactive=False
            )
            with gr.Row(elem_classes="button-row"):
                clear_btn = gr.Button("Clear", variant="primary")

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

    clear_btn.click(
        lambda: ["", ""],
        inputs=[],
        outputs=[user_input, out]
    )


tutor.launch(run_history=False)


