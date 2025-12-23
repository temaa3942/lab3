import tkinter as tk
from tkinter import filedialog, messagebox


class TextCompareApp:
    def __init__(self, root):
        self.root = root
        root.title("Сравнение текстовых файлов (LCS)")
        root.geometry("1100x650")

        self.file1_path = ""
        self.file2_path = ""

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(fill="x")

        tk.Button(top, text="Выбрать файл 1", command=lambda: self.pick_file(1)).grid(row=0, column=0, padx=(0, 8))
        tk.Button(top, text="Выбрать файл 2", command=lambda: self.pick_file(2)).grid(row=1, column=0, padx=(0, 8), pady=(6, 0))

        self.lbl1 = tk.Label(top, text="Файл 1: не выбран", anchor="w")
        self.lbl2 = tk.Label(top, text="Файл 2: не выбран", anchor="w")
        self.lbl1.grid(row=0, column=1, sticky="ew")
        self.lbl2.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        top.grid_columnconfigure(1, weight=1)

        tk.Button(top, text="Сравнить", command=self.compare).grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="ns")

        # легенда (минимально)
        legend = tk.Frame(self.root, padx=10, pady=5)
        legend.pack(fill="x")

        def box(text, color):
            tk.Label(legend, text="   ", bg=color, relief="solid", bd=1).pack(side="left", padx=(0, 6))
            tk.Label(legend, text=text).pack(side="left", padx=(0, 14))

        box("Одинаково", "#e6e6e6")
        box("Слева отличается/удалено", "#ffd6d6")
        box("Справа отличается/вставлено", "#d6ffd6")
        box("Нет строки", "#fff3b0")

        center = tk.Frame(self.root, padx=10, pady=10)
        center.pack(fill="both", expand=True)

        tk.Label(center, text="Файл 1", anchor="w").grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Label(center, text="Файл 2", anchor="w").grid(row=0, column=1, sticky="ew", padx=(5, 0))

        left_frame = tk.Frame(center)
        right_frame = tk.Frame(center)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        center.grid_columnconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)
        center.grid_rowconfigure(1, weight=1)

        self.left_text = tk.Text(left_frame, wrap="none", font=("Consolas", 10))
        self.right_text = tk.Text(right_frame, wrap="none", font=("Consolas", 10))
        self.left_text.grid(row=0, column=0, sticky="nsew")
        self.right_text.grid(row=0, column=0, sticky="nsew")

        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # общий вертикальный скролл
        vscroll = tk.Scrollbar(center, orient="vertical", command=self.yview_both)
        vscroll.grid(row=1, column=2, sticky="ns")
        self.left_text.config(yscrollcommand=vscroll.set)
        self.right_text.config(yscrollcommand=vscroll.set)

        # горизонтальные (по отдельности)
        lh = tk.Scrollbar(left_frame, orient="horizontal", command=self.left_text.xview)
        rh = tk.Scrollbar(right_frame, orient="horizontal", command=self.right_text.xview)
        lh.grid(row=1, column=0, sticky="ew")
        rh.grid(row=1, column=0, sticky="ew")
        self.left_text.config(xscrollcommand=lh.set)
        self.right_text.config(xscrollcommand=rh.set)

        # теги подсветки
        for t in (self.left_text, self.right_text):
            t.tag_configure("equal", background="#e6e6e6")
            t.tag_configure("diff_left", background="#ffd6d6")
            t.tag_configure("diff_right", background="#d6ffd6")
            t.tag_configure("missing", background="#fff3b0")
            t.config(state="disabled")

        self.status = tk.Label(self.root, text="Готово", anchor="w", padx=10)
        self.status.pack(fill="x")

    def yview_both(self, *args):
        self.left_text.yview(*args)
        self.right_text.yview(*args)

    def pick_file(self, which):
        path = filedialog.askopenfilename(
            title=f"Выберите текстовый файл {which}",
            filetypes=[("Text files", "*.txt *.csv *.log *.md"), ("All files", "*.*")]
        )
        if not path:
            return

        if which == 1:
            self.file1_path = path
            self.lbl1.config(text=f"Файл 1: {path}")
        else:
            self.file2_path = path
            self.lbl2.config(text=f"Файл 2: {path}")

        self.status.config(text=f"Выбран файл {which}")

    def read_lines(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().splitlines()
        

    def align_lcs(self, a, b):
        """Выравнивание строк через LCS. Возвращает (lineA/None, lineB/None, op)."""
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        ops = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
                ops.append((a[i - 1], b[j - 1], "equal"))
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                ops.append((None, b[j - 1], "insert"))
                j -= 1
            else:
                ops.append((a[i - 1], None, "delete"))
                i -= 1

        ops.reverse()
        return ops

    def merge_replace(self, ops):
        # делаем replace из delete+insert (чтобы было нагляднее)
        res = []
        k = 0
        while k < len(ops):
            a_line, b_line, op = ops[k]
            if op == "delete" and k + 1 < len(ops) and ops[k + 1][2] == "insert":
                res.append((a_line, ops[k + 1][1], "replace"))
                k += 2
            else:
                res.append((a_line, b_line, op))
                k += 1
        return res

    def compare(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Не выбраны файлы", "Выберите оба файла для сравнения.")
            return

        try:
            a = self.read_lines(self.file1_path)
            b = self.read_lines(self.file2_path)

            ops = self.merge_replace(self.align_lcs(a, b))

            self.left_text.config(state="normal")
            self.right_text.config(state="normal")
            self.left_text.delete("1.0", "end")
            self.right_text.delete("1.0", "end")

            ln_a = 0
            ln_b = 0
            same = 0
            diff = 0

            for la, lb, op in ops:
                if la is not None:
                    ln_a += 1
                if lb is not None:
                    ln_b += 1

                left_num = f"{ln_a:4d}" if la is not None else "    "
                right_num = f"{ln_b:4d}" if lb is not None else "    "
                left_line = la if la is not None else "(нет строки)"
                right_line = lb if lb is not None else "(нет строки)"

                left_out = f"{left_num} | {left_line}\n"
                right_out = f"{right_num} | {right_line}\n"

                l0 = self.left_text.index("end-1c")
                self.left_text.insert("end", left_out)
                l1 = self.left_text.index("end-1c")

                r0 = self.right_text.index("end-1c")
                self.right_text.insert("end", right_out)
                r1 = self.right_text.index("end-1c")

                if op == "equal":
                    self.left_text.tag_add("equal", l0, l1)
                    self.right_text.tag_add("equal", r0, r1)
                    same += 1
                elif op == "delete":
                    self.left_text.tag_add("diff_left", l0, l1)
                    self.right_text.tag_add("missing", r0, r1)
                    diff += 1
                elif op == "insert":
                    self.left_text.tag_add("missing", l0, l1)
                    self.right_text.tag_add("diff_right", r0, r1)
                    diff += 1
                else:  # replace
                    self.left_text.tag_add("diff_left", l0, l1)
                    self.right_text.tag_add("diff_right", r0, r1)
                    diff += 1

            self.left_text.config(state="disabled")
            self.right_text.config(state="disabled")
            self.status.config(text=f"Готово. Одинаковых: {same}, отличий/вставок/удалений: {diff}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не получилось сравнить файлы:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    TextCompareApp(root)
    root.mainloop()
