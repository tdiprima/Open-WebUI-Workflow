from typing import List

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Example valve: Adding a sample configuration
        # example_parameter: Optional[str] = None  # Add a configurable parameter
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def calculator(self, equation: str) -> str:
            """
            Calculate the result of an equation.
            :param equation: The equation to calculate.
            """
            print(f"Calculator called with equation: {equation}")
            try:
                result = eval(equation)
                print(f"Calculation result: {result}")
                return f"{equation} = {result}"
            except Exception as e:
                print(f"Error in calculator: {e}")
                return "Invalid equation"

    def __init__(self):
        super().__init__()
        self.name = "My Calculator Tool Pipeline"
        self.valves = self.Valves(**{**self.valves.model_dump(), "pipelines": ["*"],  # Connect to all pipelines
        }, )
        self.tools = self.Tools(self)

    async def on_startup(self):
        print(f"on_startup: {__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown: {__name__}")

    # def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict):
    #     print(f"Pipe called with message: {user_message}")
    #     print(f"Model ID: {model_id}")
    #     return "Debugging response"
