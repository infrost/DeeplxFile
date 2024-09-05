import sys
import io

class RedirectText(io.StringIO):
    def __init__(self, text_widget, tag):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag

    def write(self, message):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        self.text_widget.insert('end', message, self.tag)
        self.text_widget.see('end')  # 自动滚动到文本框的底部

    def flush(self):
        pass  # flush方法可以留空

def start_redirect(text_widget):
    redirector_out = RedirectText(text_widget, "default")
    redirector_err = RedirectText(text_widget, "error")
    sys.stdout = redirector_out
    sys.stderr = redirector_err

def send_warning(text_widget, message):
    text_widget.insert('end', message + '\n', 'warning')
    text_widget.see('end') 

def success_message(text_widget, message):
    text_widget.insert('end', message + '\n', 'success')
    text_widget.see('end') 
