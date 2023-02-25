import json
import time

from Login import SSO, Login

sso = None


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
        elif isinstance(_id, int):
            self.now:Node = self.now.children[_id]
        else:
            print("Wrong id input")
        if not self.now.inited:
            self.now.init()


if __name__ == "__main__":
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

    cdid = int(input("id: "))
    cd_start = time.time()
    fs.cd(cdid)
    print(f"cd并获取新内容耗时: {time.time()-cd_start}")
    print(fs.ls())
    print(fs.now.getPath())

