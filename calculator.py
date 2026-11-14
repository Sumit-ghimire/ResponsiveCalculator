
import tkinter as tk
import ast
import operator
import math
import re

BG = "#F3F5F9"
DISPLAY_BG = "#FFFFFF"
NUMBER_BG = "#FFFFFF"
SPECIAL_BG = "#E8ECF4"
OPERATOR_BG = "#DCE8FF"
EQUAL_BG = "#2864E8"
TEXT_COLOR = "#202A44"
BLUE = "#2864E8"
WHITE = "#FFFFFF"

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Calculator")
        self.root.geometry("420x650")
        self.root.minsize(320, 480)
        self.root.configure(bg=BG)

        self.expression = ""
        self.result = ""

        self.create_display()
        self.create_buttons()
        self.bind_keyboard()

        self.root.bind("<Configure>", self.resize_fonts)

    def create_display(self):
        self.display_frame = tk.Frame(
            self.root, bg=DISPLAY_BG, padx=20, pady=20
        )
        self.display_frame.pack(fill="both", expand=False, padx=12, pady=12)

        self.history_label = tk.Label(
            self.display_frame,
            text="",
            bg=DISPLAY_BG,
            fg="#9299A8",
            anchor="e",
            font=("Arial", 14)
        )
        self.history_label.pack(fill="x", pady=10)

        self.display_label = tk.Label(
            self.display_frame,
            text="0",
            bg=DISPLAY_BG,
            fg=TEXT_COLOR,
            anchor="e",
            font=("Arial", 36, "bold")
        )
        self.display_label.pack(fill="x", pady=10)

    def create_buttons(self):
        self.buttons_frame = tk.Frame(self.root, bg=BG)
        self.buttons_frame.pack(
            fill="both", expand=True, padx=12, pady=8
        )

        buttons = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
            ["x²", "√x", "(", ")"]
        ]

        self.button_widgets = []

        for row_index, row in enumerate(buttons):
            self.buttons_frame.rowconfigure(row_index, weight=1)

            for col_index, text in enumerate(row):
                self.buttons_frame.columnconfigure(col_index, weight=1)

                if text == "=":
                    bg = EQUAL_BG
                    fg = WHITE
                elif text in ["÷", "×", "-", "+"]:
                    bg = OPERATOR_BG
                    fg = BLUE
                elif text in ["C", "⌫", "%", "±", "x²", "√x", "(", ")"]:
                    bg = SPECIAL_BG
                    fg = TEXT_COLOR
                else:
                    bg = NUMBER_BG
                    fg = TEXT_COLOR

                button = tk.Button(
                    self.buttons_frame,
                    text=text,
                    bg=bg,
                    fg=fg,
                    font=("Arial", 20, "bold"),
                    relief="flat",
                    borderwidth=0,
                    activebackground=bg,
                    command=lambda value=text: self.button_click(value)
                )

                button.grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

                self.button_widgets.append(button)

    def button_click(self, value):
        if value == "C":
            self.clear()

        elif value == "⌫":
            self.backspace()

        elif value == "=":
            self.calculate()

        elif value == "±":
            self.toggle_sign()

        elif value == "%":
            self.percentage()

        elif value == "x²":
            self.square()

        elif value == "√x":
            self.square_root()

        else:
            symbols = {
                "÷": "/",
                "×": "*"
            }

            value = symbols.get(value, value)

            if len(self.expression) < 100:
                self.expression += value

            self.update_display()

    def clear(self):
        self.expression = ""
        self.result = ""
        self.history_label.config(text="")
        self.update_display()

    def backspace(self):
        self.expression = self.expression[:-1]
        self.update_display()

    def toggle_sign(self):
        match = re.search(r"(\d+\.?\d*|\.\d+)$", self.expression)

        if match:
            start = match.start()
            number = match.group()

            if start > 0 and self.expression[start - 1] == "-":
                self.expression = (
                    self.expression[:start - 1] + number
                )
            else:
                self.expression = (
                    self.expression[:start] + "-" + number
                )

        self.update_display()

    def percentage(self):
        match = re.search(r"(\d+\.?\d*|\.\d+)$", self.expression)

        if match:
            number = float(match.group()) / 100
            self.expression = (
                self.expression[:match.start()] + str(number)
            )

        self.update_display()

    def square(self):
        try:
            value = self.safe_calculate(self.expression)
            self.expression = str(value ** 2)
            self.update_display()
        except Exception:
            self.show_error()

    def square_root(self):
        try:
            value = self.safe_calculate(self.expression)

            if value < 0:
                raise ValueError("Invalid square root")

            self.expression = str(math.sqrt(value))
            self.update_display()
        except Exception:
            self.show_error()

    def safe_calculate(self, expression):
        expression = expression.replace("×", "*").replace("÷", "/")

        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg
        }

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value
                raise ValueError("Invalid number")

            if isinstance(node, ast.BinOp):
                op_type = type(node.op)

                if op_type not in allowed_operators:
                    raise ValueError("Invalid operator")

                left = evaluate(node.left)
                right = evaluate(node.right)

                if op_type == ast.Pow and abs(right) > 10:
                    raise ValueError("Exponent too large")

                result = allowed_operators[op_type](left, right)

                if not math.isfinite(result) or abs(result) > 1e100:
                    raise ValueError("Result too large")

                return result

            if isinstance(node, ast.UnaryOp):
                op_type = type(node.op)

                if op_type not in allowed_operators:
                    raise ValueError("Invalid operator")

                return allowed_operators[op_type](
                    evaluate(node.operand)
                )

            raise ValueError("Invalid expression")

        if not expression:
            raise ValueError("Empty expression")

        tree = ast.parse(expression, mode="eval")
        return evaluate(tree)

    def calculate(self):
        if not self.expression:
            return

        try:
            original = self.expression
            answer = self.safe_calculate(original)

            if isinstance(answer, float):
                answer = round(answer, 10)

            self.history_label.config(text=original + " =")
            self.expression = str(answer)
            self.result = str(answer)

            self.update_display()

        except Exception:
            self.show_error()

    def show_error(self):
        self.expression = ""
        self.history_label.config(text="Invalid calculation")
        self.display_label.config(text="Error")

    def update_display(self):
        display = self.expression.replace("*", "×").replace("/", "÷")
        self.display_label.config(
            text=display if display else "0"
        )

    def bind_keyboard(self):
        self.root.bind("<Return>", lambda event: self.calculate())
        self.root.bind("<KP_Enter>", lambda event: self.calculate())
        self.root.bind("<BackSpace>", lambda event: self.backspace())
        self.root.bind("<Escape>", lambda event: self.clear())

        for key in "0123456789.+-*/()%":
            self.root.bind(
                key,
                lambda event, value=key: self.add_keyboard(value)
            )

    def add_keyboard(self, value):
        if len(self.expression) < 100:
            self.expression += value
            self.update_display()

    def resize_fonts(self, event):
        if event.widget != self.root:
            return

        width = self.root.winfo_width()
        size = max(12, min(25, int(width / 17)))

        for button in self.button_widgets:
            button.config(font=("Arial", size, "bold"))

        self.display_label.config(
            font=("Arial", max(24, min(42, width // 10)), "bold")
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    calculator.run()
