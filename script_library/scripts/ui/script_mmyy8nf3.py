import ui
import math

class CalculatorView(ui.View):
    def __init__(self):
        super().__init__()  # 添加父类初始化调用
        self.name = '计算器'
        self.background_color = 'black'
        self.display_text = '0'
        self.first_operand = None
        self.operator = None
        self.waiting_for_second_operand = False
        self.should_reset_display = False
        
        # 按钮布局和标签 - 存储为实例变量以便 layout() 访问
        self.button_specs = [
            ('AC', 0, 0, 1), ('⌫', 1, 0, 1), ('%', 2, 0, 1), ('÷', 3, 0, 1),
            ('7', 0, 1, 1), ('8', 1, 1, 1), ('9', 2, 1, 1), ('×', 3, 1, 1),
            ('4', 0, 2, 1), ('5', 1, 2, 1), ('6', 2, 2, 1), ('-', 3, 2, 1),
            ('1', 0, 3, 1), ('2', 1, 3, 1), ('3', 2, 3, 1), ('+', 3, 3, 1),
            ('0', 0, 4, 2), ('.', 2, 4, 1), ('=', 3, 4, 1)
        ]
        
        # 创建显示标签
        self.display_label = ui.Label()
        self.display_label.text = self.display_text
        self.display_label.font = ('<system>', 40)
        self.display_label.text_color = 'white'
        self.display_label.alignment = ui.ALIGN_RIGHT
        self.display_label.number_of_lines = 1
        self.display_label.flex = 'W'
        
        # 创建按钮
        self.buttons = {}
        for text, col, row, col_span in self.button_specs:
            btn = ui.Button(title=text)
            btn.font = ('<system>', 28)
            btn.background_color = self.get_button_color(text)
            btn.tint_color = 'white'
            btn.corner_radius = 40
            btn.action = self.button_tapped
            self.buttons[text] = btn
            self.add_subview(btn)
        
        self.add_subview(self.display_label)
    
    def get_button_color(self, text):
        # 数字和点按钮为深灰色
        if text in '0123456789.':
            return (0.2, 0.2, 0.2, 1)  # 深灰
        # 操作符按钮为橙色
        elif text in '÷×-+=':
            return (1.0, 0.6, 0.0, 1)  # 橙色
        # 功能按钮为浅灰色
        else:
            return (0.5, 0.5, 0.5, 1)  # 浅灰
    
    def layout(self):
        # 设置显示标签位置
        display_height = 120
        self.display_label.frame = (20, 40, self.width - 40, display_height)
        
        # 设置按钮位置
        button_size = 80
        button_margin = 10
        start_y = display_height + 60
        
        for text, btn in self.buttons.items():
            # 找到按钮在布局中的位置
            for spec_text, col, row, col_span in self.button_specs:
                if spec_text == text:
                    x = 20 + col * (button_size + button_margin)
                    y = start_y + row * (button_size + button_margin)
                    width = button_size * col_span + button_margin * (col_span - 1)
                    btn.frame = (x, y, width, button_size)
                    break
    
    def button_tapped(self, sender):
        text = sender.title
        
        if text in '0123456789':
            self.input_digit(text)
        elif text == '.':
            self.input_decimal()
        elif text in '÷×-+':
            self.set_operation(text)
        elif text == '=':
            self.calculate_result()
        elif text == 'AC':
            self.clear_all()
        elif text == '±':
            self.toggle_sign()
        elif text == '⌫':
            self.delete_last()
        elif text == '%':
            self.calculate_percentage()
    
    def input_digit(self, digit):
        if self.display_text == '0' or self.waiting_for_second_operand or self.should_reset_display:
            self.display_text = digit
            self.waiting_for_second_operand = False
            self.should_reset_display = False
        else:
            self.display_text += digit
        
        self.update_display()
    
    def input_decimal(self):
        if self.waiting_for_second_operand or self.should_reset_display:
            self.display_text = '0.'
            self.waiting_for_second_operand = False
            self.should_reset_display = False
        elif '.' not in self.display_text:
            self.display_text += '.'
        
        self.update_display()
    
    def set_operation(self, op):
        if self.operator is not None and not self.waiting_for_second_operand:
            self.calculate_result()
        
        try:
            self.first_operand = float(self.display_text)
        except:
            self.first_operand = 0
        
        self.operator = op
        self.waiting_for_second_operand = True
        self.should_reset_display = True
    
    def calculate_result(self):
        if self.operator is None or self.waiting_for_second_operand:
            return
        
        try:
            second_operand = float(self.display_text)
            
            if self.operator == '+':
                result = self.first_operand + second_operand
            elif self.operator == '-':
                result = self.first_operand - second_operand
            elif self.operator == '×':
                result = self.first_operand * second_operand
            elif self.operator == '÷':
                if second_operand == 0:
                    self.display_text = '错误'
                    self.update_display()
                    self.clear_all()
                    return
                result = self.first_operand / second_operand
            
            # 处理浮点数精度问题
            if result.is_integer():
                self.display_text = str(int(result))
            else:
                # 限制小数位数
                self.display_text = f'{result:.10f}'.rstrip('0').rstrip('.')
            
            self.first_operand = result
            self.operator = None
            self.waiting_for_second_operand = True
            self.should_reset_display = True
            self.update_display()
            
        except Exception as e:
            self.display_text = '错误'
            self.update_display()
            self.clear_all()
    
    def clear_all(self):
        self.display_text = '0'
        self.first_operand = None
        self.operator = None
        self.waiting_for_second_operand = False
        self.should_reset_display = False
        self.update_display()
    
    def toggle_sign(self):
        try:
            value = float(self.display_text)
            value = -value
            if value.is_integer():
                self.display_text = str(int(value))
            else:
                self.display_text = str(value)
            self.update_display()
        except:
            pass
    
    def delete_last(self):
        if self.display_text != '0' and len(self.display_text) > 1:
            self.display_text = self.display_text[:-1]
        elif len(self.display_text) == 1:
            self.display_text = '0'
        self.update_display()
    
    def calculate_percentage(self):
        try:
            value = float(self.display_text)
            value = value / 100
            if value.is_integer():
                self.display_text = str(int(value))
            else:
                self.display_text = str(value)
            self.update_display()
        except:
            pass
    
    def update_display(self):
        # 限制显示长度
        if len(self.display_text) > 12:
            if '.' in self.display_text:
                self1.display_text = self.display_text[:12]
            else:
                self.display_text = self.display_text[:12]
        
        self.display_label.text = self.display_text

# 运行计算器
if __name__ == '__main__':
    view = CalculatorView()
    view.present('fullscreen')