import logging
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

class CommandLineInterface:
    def __init__(self):
        self.history = FileHistory('kamil_cli_history.txt')
        self.logger = logging.getLogger("CLI")
        self.chat_history = []

    def start(self, agent):
        print("Kamil CLI - Type 'exit' to quit\n")
        
        # Create autocompletion for common commands
        commands = ['exit', 'help', 'clear history', 'show memory', 'run tool']
        completer = WordCompleter(commands, ignore_case=True)
        
        while True:
            try:
                user_input = prompt(
                    "You: ",
                    history=self.history,
                    auto_suggest=AutoSuggestFromHistory(),
                    mouse_support=True,
                    completer=completer
                )
                
                if user_input.strip().lower() == "exit":
                    print("Goodbye!")
                    break
                elif user_input.strip().lower() == "clear history":
                    self.chat_history = []
                    print("Chat history cleared")
                    continue
                
                response = agent.process_request(user_input, history=self.chat_history)
                print(f"\nKamil: {response}\n")
                
                # Store interaction
                self.chat_history.append((user_input, response))
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                self.logger.error(f"CLI error: {str(e)}")
                print("An error occurred. Please try again.")
