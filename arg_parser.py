import argparse

class arg_parser:
    @staticmethod
    def parser():
        parser = argparse.ArgumentParser(description="bot_parser")
        parser.add_argument("--app", type=str, default='dingtalk', help="app you want to deploy your bot on")
        parser.add_argument('--debug', action='store_true', help='Add this flag if in debug mode,'
                                                                 'the program will use testing accounts')
        args = parser.parse_args()
        if args.app == 'dingtalk':
            import dingtalk_receive.Receive as Receive
        else:
            import qq_receive.Receive as Receive