"""Run the workspace with Python, or render it inside the Streamlit server."""


def main():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        in_streamlit = get_script_run_ctx(suppress_warning=True) is not None
    except ImportError:
        in_streamlit = False

    if not in_streamlit:
        from run import main as launch_application

        return launch_application()

    from frontend.app import main as render_workspace

    render_workspace()
    return 0


if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        raise SystemExit(exit_code)
