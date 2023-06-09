import requests
from urllib.parse import urljoin
import urllib3
import json
import sys
import os
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#! file name
fnafr=sys.argv[0].split('.')[0]
##! Config file path
conf_file = fnafr+".conf"
config = ConfigParser()
config.read(conf_file)

try:
    CredentialInfo = config["Credentials"]
    ModelInfo = config["Models"]
    MiscInfo = config["misc"]
    SysInfo = config["System"]
    ChatInfo = config["Chat"]
    ImageInfo = config["Image"]
    AudioInfo = config["Audio"]
except KeyError:
    sys.exit("Error found in the configuration file.")

#? Creds
API_KEY = CredentialInfo["API_KEY"]
#? Config Info
chat_model = ModelInfo["chat_model"]
audio_model = ModelInfo["audio_model"]
#? System Info
sys_msg = SysInfo["sys_msg"]
#? Chat Info
chat_temp = float(ChatInfo["chat_temperature"])
#? Audio Info
audio_b_temp = AudioInfo["audio_transcrb_temperature"]
audio_l_temp = AudioInfo["audio_translt_temperature"]
#? Image Info
new_image_size = ImageInfo["new_image_size"]
edit_image_size = ImageInfo["edit_image_size"]
var_image_size = ImageInfo["var_image_size"]
new_image_format = ImageInfo["new_image_format"]
edit_image_format = ImageInfo["edit_image_format"]
var_image_format = ImageInfo["var_image_format"]
#? misc
API_URL = MiscInfo["API_URL"]

def gpt_req(mod, chat, ssl_ver = True):
    data = {
        "model": mod,
        "messages": chat,
        "temperature": chat_temp
        }
    api_path = 'v1/chat/completions'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, json=data, verify = ssl_ver)
    return r

def new_img(num, pr, ssl_ver = True):
    data = {
        "prompt":  pr,
        "n": num,
        "size": new_image_size,
        'response_format': new_image_format
        }
    api_path = 'v1/images/generations'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, json=data, verify = ssl_ver)
    return r

def edit_img(num, img, mask, pr, ssl_ver = True):
    files = {
        'image': open(img, 'rb'),
        'mask': open(mask, 'rb'),
        'prompt': (None, pr),
        'n': (None, num),
        'size': (None, edit_image_size),
        'response_format': (None, edit_image_format),
        }
    api_path = 'v1/images/edits'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, files=files, verify = ssl_ver)
    return r

def var_img(num, img, ssl_ver = True):
    files = {
        'image': open(img, 'rb'),
        'n': (None, num),
        'size': (None, var_image_size),
        'response_format': (None, var_image_format),
        }
    api_path = 'v1/images/variations'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, files=files, verify = ssl_ver)
    return r

def transcrb(voice, ssl_ver = True):
    files = {
        'file': open(voice, 'rb'),
        'model': (None, audio_model),
        'temperature': (None, audio_b_temp),
        }
    api_path = 'v1/audio/transcriptions'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, files=files, verify = ssl_ver)
    return r

def transl(voice, ssl_ver = True):
    files = {
        'file': open(voice, 'rb'),
        'model': (None, audio_model),
        'temperature': (None, audio_l_temp),
        }
    api_path = 'v1/audio/translations'
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.post(urljoin(API_URL,api_path), headers=headers, files=files, verify = ssl_ver)
    return r

def get_model(mod, ssl_ver = True):
    api_path = f"v1/models/{mod}"
    AUTH = 'Bearer '+ API_KEY
    headers = {'Content_type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': AUTH}
    r = requests.get(urljoin(API_URL,api_path), headers=headers, verify = ssl_ver)
    return r

def input_message():
    message_in = ""
    try:
        while message_in == "":
            message_in = input("Message: ")
            if message_in == "exit":
                sys.exit("Exiting...")
        return message_in
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
        
def input_opt():
    global opt_in
    opt_in = 0
    try:
        while int(opt_in) < 1 or int(opt_in) > 6:
            print("Options available:\n1: Chat\n2: Generate New Image\n3: Generate Image Edits\n4: Generate Image Variations\n5: Generate Audio Transcription\n6: Generate Audio Translation\n")
            opt_in = int(input("Option: "))
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
        
def input_num():
    global num_in
    num_in = 0
    verr = False
    try:
        while int(num_in) < 1 or int(num_in) > 10 or verr:
            try:
                num_in = int(input(f"Number of images to generate: "))
                verr = False
            except ValueError:
                verr = True
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")

def input_pr():
    global pr_in
    pr_in = ""
    try:
        while pr_in == "":
            pr_in = input(f"Prompt: ")
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
         
def input_img():
    global img_in     
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.attributes('-alpha',0.01)
    root.attributes('-topmost',True)
    root.tk.eval(f'tk::PlaceWindow {root._w} center')
    root.withdraw()
    f_types = [('PNG Files', '*.png')]
    size = 99
    try:
        while size > 4:
            print(f"Upload an image (PNG, <4MB)")
            img_in = filedialog.askopenfilename(filetypes=f_types)
            file_stats = os.stat(img_in)
            size = file_stats.st_size / (1024 * 1024)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
        
def input_mask():
    global mask_in          
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.attributes('-alpha',0.01)
    root.attributes('-topmost',True)
    root.tk.eval(f'tk::PlaceWindow {root._w} center')
    root.withdraw()
    f_types = [('PNG Files', '*.png')]
    size = 99
    try:
        while size > 4:
            print(f"Upload a mask (PNG, <4MB)")
            mask_in = filedialog.askopenfilename(filetypes=f_types)
            file_stats = os.stat(mask_in)
            size = file_stats.st_size / (1024 * 1024)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
        
def input_audio():
    global audio_in          
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.attributes('-alpha',0.01)
    root.attributes('-topmost',True)
    root.tk.eval(f'tk::PlaceWindow {root._w} center')
    root.withdraw()
    f_types = [('Audio Files', '*.mp3 *.mp4 *.mpeg *.mpga *.m4a *.wav *.webm')]
    try:
        print(f"Upload an audio file (mp3, mp4, mpeg, mpga, m4a, wav, or webm)")
        audio_in = filedialog.askopenfilename(filetypes=f_types)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as E:
        sys.exit(f"{E}")
    
def convo():
    global gpt_response
    #! Write message
    msg = input_message()
    #! Add message to convo
    msg_list.append({"role": "user", "content": msg})
    gpt_response = gpt_req(chat_model, msg_list, False)
    if gpt_response.ok:
        gpt_answer_role = json.loads(gpt_response.content)["choices"][0]["message"]
        gpt_answer = gpt_answer_role["content"]
        print(f"Response:\n\n {gpt_answer}\n")
        msg_list.append(gpt_answer_role)
        convo()
    else:
        sys.exit(f"Error message: {json.loads(gpt_response.content)['error']['message']}\nExiting...")

if __name__ == "__main__":
    #! Choose option
    input_opt()
    if opt_in == 1:
        #! Initiate message list
        msg_list = [
            {"role": "system", "content": sys_msg}
        ]
        #! Verify model
        model_resp = get_model(chat_model, False)
        if not model_resp.ok:
            sys.exit(f"Error message: {json.loads(model_resp.content)['error']['message']}\nExiting...")
        #! Start convo
        convo()
    elif opt_in == 2:
        input_pr()
        input_num()
        new_img_resp = new_img(num_in, pr_in, False)
        if new_img_resp.ok:
            new_imgs = json.loads(new_img_resp.content)["data"]
            if len(new_imgs) > 0:
                print(f"Generated {len(new_imgs)} images:")
                for i in new_imgs:
                    print(f"- {i[list(i.keys())[0]]}")
        else:
            sys.exit(f"Error message: {json.loads(new_img_resp.content)['error']['message']}\nExiting...")
    elif opt_in == 3:
        input_pr()
        input_num()
        input_img()
        input_mask()
        edit_img_resp = edit_img(num_in, img_in, mask_in, pr_in, False)
        if edit_img_resp.ok:
            new_imgs = json.loads(edit_img_resp.content)["data"]
            if len(new_imgs) > 0:
                print(f"Generated {len(new_imgs)} images:")
                for i in new_imgs:
                    print(f"- {i[list(i.keys())[0]]}")
        else:
            sys.exit(f"Error message: {json.loads(edit_img_resp.content)['error']['message']}\nExiting...")
    elif opt_in == 4:
        input_num()
        input_img()
        var_img_resp = var_img(num_in, img_in, False)
        if var_img_resp.ok:
            new_imgs = json.loads(var_img_resp.content)["data"]
            if len(new_imgs) > 0:
                print(f"Generated {len(new_imgs)} images:")
                for i in new_imgs:
                    print(f"- {i[list(i.keys())[0]]}")
        else:
            sys.exit(f"Error message: {json.loads(var_img_resp.content)['error']['message']}\nExiting...")
    elif opt_in == 5:
        input_audio()
        trans_resp = transcrb(audio_in, False)
        if trans_resp.ok:
            trans_txt = json.loads(trans_resp.content)["text"]
            print(f"Generated transcription:\n\n {trans_txt}\n")
        else:
            sys.exit(f"Error message: {json.loads(trans_resp.content)['error']['message']}\nExiting...")
    elif opt_in == 6:
        input_audio()
        transl_resp = transl(audio_in, False)
        if transl_resp.ok:
            trans_txt = json.loads(transl_resp.content)["text"]
            print(f"Generated translation:\n\n {trans_txt}\n")
        else:
            sys.exit(f"Error message: {json.loads(transl_resp.content)['error']['message']}\nExiting...")

    