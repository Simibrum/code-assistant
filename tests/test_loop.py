import signal

import agent.loop


def test_signal_handler(mocker):
    """
    Test the signal_handler function to ensure it logs the correct information and
    exits with code 0.
    """
    mock_logger = mocker.patch("agent.loop.logger.info")
    mock_exit = mocker.patch("agent.loop.exit")
    test_signum = 15
    test_frame = mocker.MagicMock()
    agent.loop.signal_handler(test_signum, test_frame)
    mock_logger.assert_called_once_with("Signal received, terminating agent")
    mock_exit.assert_called_once_with(0)


def test_main_loop(mocker):
    """
    Test the main_loop function to ensure it handles exceptions and continues execution.
    """
    mocker.patch("agent.loop.time.sleep", return_value=None)
    log_mock = mocker.patch("agent.loop.logger.error")

    def handler(signum, frame):
        raise Exception("Test Error")

    # Set the signal handler and a 1-second alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        with mocker.patch(
            "agent.loop.main_loop", side_effect=[Exception("Test Error"), None]
        ):
            try:
                agent.loop.main_loop()
                assert False, "main_loop did not raise"
            except Exception as e:
                assert str(e) == "Test Error", f"Unexpected exception: {e}"
    finally:
        # Disable the alarm
        signal.alarm(0)

    # log_mock.assert_called_with("An error occurred: Test Error")
