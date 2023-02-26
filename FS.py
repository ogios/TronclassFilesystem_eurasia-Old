import json
import random
import time
import os
import traceback
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from Login import SSO, Login
from tempzip import compress

sso = SSO({})
PATH = os.path.dirname(__file__) + "/downloads/"
if not os.path.exists(PATH):
    os.mkdir(PATH)

class Node:
    def __init__(self, id: int, name: str, is_dir: bool, filesize: int, children: dict, parent):
        self.id = id
        self.name = name
        self.is_dir = is_dir
        self.filesize = filesize
        self.children = children
        self.parent = parent
        self.inited = False

    def __repr__(self):
        if self.parent is None:
            return ""
        else:
            return f"{self.parent}/{self.name}"

    def getPath(self):
        if self.parent is None:
            return ""
        else:
            return f"{self.parent.getPath()}/{self.name}"

    def init(self):
        dirs = getDirs(self)
        files = getFiles(self)
        self.children.update(dirs)
        self.children.update(files)
        self.inited = True

    def download(self):
        if self.is_dir:
            return "文件夹无法下载"
        else:
            try:
                url = f"http://lms.eurasia.edu/api/uploads/{self.id}/blob"
                res = sso.get(url, allow_redirects=False)
                location = res.headers.get("Location", None)
                if location:
                    res = sso.get(location, stream=True)
                    with open(PATH + self.name, "wb") as f:
                        for cont in res.iter_content(10240):
                            f.write(cont)
                    return f"{self.name} - 下载完成。"
            except Exception as e:
                return f"{self.name} - 下载失败！"



def addNode(uploads: list, nodes: dict, parent: Node):
    for i in uploads:
        nodes[i["id"]] = Node(
            id=i["id"],
            name=i["name"],
            is_dir=i["is_folder"],
            filesize=i["size"],
            children=dict(),
            parent=parent
        )
    return nodes


def getDirs(node: Node) -> dict:
    '''
    获取文件夹下的所有文件夹
    '''
    children = dict()
    url = "http://lms.eurasia.edu/api/user/resources"
    condition = {
        "keyword": "",
        "includeSlides": False,
        "limitTypes": ["folder"],
        "fileType": "all",
        "parentId": node.id,
        "sourceType": "MyResourcesFolder",
        "no-intercept": True
    }
    params = {
        "conditions": json.dumps(condition),
        "page": 1,
        "page_size": 20,
    }
    firstPage = sso.get(url, params=params)
    js_first = json.loads(firstPage.text)
    children = addNode(js_first["uploads"], children, node)
    for _ in range(js_first["pages"] - 1):
        params["page"] += 1
        page = sso.get(url, params=params)
        js = json.loads(page.text)
        children = addNode(js["uploads"], children, node)
    return children


def getFiles(node: Node) -> dict:
    '''
    获取文件夹下的所有文件
    '''
    children = dict()
    url = "http://lms.eurasia.edu/api/user/resources"
    condition = {
        "keyword": "",
        "includeSlides": False,
        "limitTypes": ["file", "video", "document", "image", "audio", "scorm", "evercam", "swf", "wmpkg", "link"],
        "fileType": "all",
        "parentId": node.id,
        "sourceType": "MyResourcesFile",
        "no-intercept": True
    }
    params = {
        "conditions": json.dumps(condition),
        "page": 1,
        "page_size": 20,
    }
    firstPage = sso.get(url, params=params)
    js_first = json.loads(firstPage.text)
    children = addNode(js_first["uploads"], children, node)
    for _ in range(js_first["pages"] - 1):
        params["page"] += 1
        page = sso.get(url, params=params)
        js = json.loads(page.text)
        children = addNode(js["uploads"], children, node)
    return children

def uplaodFile(filename, parentid):
    assert os.path.exists(filename)

    url = "http://lms.eurasia.edu/api/uploads"
    size = os.path.getsize(filename)
    data = {
        "name": os.path.basename(filename),
        "size": size,
        "parent_id": parentid,
        "is_scorm": False,
        "is_wmpkg": False,
        "source": "",
        "is_marked_attachment": False,
        "embed_material_type": ""
    }

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
    }
    res = sso.post(url, data=json.dumps(data), headers=headers)
    js = json.loads(res.text)

    upload_url = js["upload_url"]
    requests.options(upload_url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
    }
    multipart = MultipartEncoder(
        fields={
            "file": (os.path.basename(filename), open(filename, "rb"), "application/octet-stream")
        },
        boundary="-----------------------------" + str(random.randint(1e28, 1e29 - 1))
    )
    headers["Content-Type"] = multipart.content_type
    res = requests.put(upload_url, data=multipart, headers=headers)
    js: dict = json.loads(res.text)
    if js.__contains__("file_key"):
        return 1
    elif (js.__contains__("error")) & (js["error"] == "Invalid file type."):
        return 2
    else:
        raise Exception(res.text)


class FS:
    def __init__(self):
        self.root = Node(id=0, name="root", is_dir=True, filesize=0, children=dict(), parent=None)
        self.now:Node = self.root
        # sso.get("http://lms.eurasia.edu/center/static/js/wg-apps.js")
        self.root.init()
        sso.get("http://lms.eurasia.edu/center/api/users/20338209150460/apps-panel-settings")
        # sso.get("http://lms.eurasia.edu/center/api/users/20338209150460/permissions")
        print(sso.getCookies())

    def ls(self):
        return self.now.children

    def cd(self, _id):
        if (_id == "..") & (self.now.parent is not None):
            self.now:Node = self.now.parent
        elif isinstance(_id, int) and self.now.children[_id].is_dir:
            self.now:Node = self.now.children[_id]
        else:
            print("Wrong id input")
        if not self.now.inited:
            self.now.init()

    def upload(self, filename):
        """
        上传文件
        """
        # assert os.path.exists(filename)
        # """获取上传链接"""
        # url = "http://lms.eurasia.edu/api/uploads"
        # size = os.path.getsize(filename)
        # data = {
        #     "name": os.path.basename(filename),
        #     "size": size,
        #     "parent_id": self.now.id,
        #     "is_scorm": False,
        #     "is_wmpkg": False,
        #     "source":"",
        #     "is_marked_attachment": False,
        #     "embed_material_type":""
        # }
        #
        # headers = {
        #     "Content-Type": "application/json;charset=UTF-8",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
        # }
        # res = sso.post(url, data=json.dumps(data), headers=headers)
        # js = json.loads(res.text)

        """上传文件"""
        try:
            # upload_url = js["upload_url"]
            # requests.options(upload_url)
            uploadStatus = uplaodFile(filename, self.now.id)
            if uploadStatus == 1:
                self.now.init()
                return "上传完成"
            elif uploadStatus == 2:
                print("格式不支持，正在压缩...")
                compressStatus = compress(filename)
                if (compressStatus != 0) & (compressStatus != 2):
                    print(compressStatus)
                    uploadStatus = uplaodFile(compressStatus, self.now.id)
                    if uploadStatus == 1:
                        self.now.init()
                        return "上传完成"
                    else:
                        return f"上传失败 - {uploadStatus}"
                else:
                    return f"压缩失败 - {compressStatus}"

        except Exception as e:
            traceback.print_exc()






def test():
    global sso
    login_start = time.time()
    username = 学号
    password = 密码
    login = Login(username, password)
    sso = login.login()
    print(f"登录耗时: {time.time()-login_start}")

    fs_start = time.time()
    fs = FS()
    print(f"文件系统创建耗时: {time.time()-fs_start}")
    print(fs.ls())
    print(fs.now.getPath())

    while 1:
        cmd = input(">>>").split()
        if cmd[0] == "ls":
            print(fs.ls())
        elif cmd[0] == "cd":
            try:
                if cmd[-1] == "..":
                    cdid = cmd[-1]
                else:
                    cdid = int(cmd[-1])
                cd_start = time.time()
                fs.cd(cdid)
                print(f"cd并获取新内容耗时: {time.time()-cd_start}")
            except Exception as e:
                traceback.print_exc()
        elif cmd[0] == "get":
            try:
                getid = int(cmd[-1])
                get_start = time.time()
                print(fs.now.children[getid].download())
                print(f"下载内容耗时: {time.time() - get_start}")
            except Exception as e:
                traceback.print_exc()
        elif cmd[0] == "upload":
            try:
                filename = "".join(cmd[1:])
                print(filename)
                upload_start = time.time()
                print(fs.upload(filename))
                print(f"上传内容耗时: {time.time() - upload_start}")
            except Exception as e:
                traceback.print_exc()
        elif cmd[0] == "reload":
            fs.now.init()



if __name__ == "__main__":
    test()

