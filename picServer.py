def takePic(sock):
        pic = pyautogui.screenshot()
        fd = io.BytesIO()
        pic.save(fd, "png")
        data = fd.getvalue()
        sock.sendJSon(data)
