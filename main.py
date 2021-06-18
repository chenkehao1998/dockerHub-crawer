from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = None

def main():
    for i in range(7,10):
        getPageData(i)

def getPageData(pageindex):
    global browser
    browser = webdriver.Chrome(options=chrome_options)
    # browser = webdriver.Chrome()
    url = f'https://hub.docker.com/search?type=image&page={pageindex}'
    print(url)
    browser.get(url)
    now_handle = browser.current_window_handle
    browser.implicitly_wait(20)  # 智能等待20秒
    itemElements = browser.find_elements_by_xpath(r"//div[@id='searchResults']/div/a")

    imageList = []

    for itemElement in itemElements:
        browser.switch_to.window(now_handle)  # 切换到原来的窗口
        nameElement = itemElement.find_element_by_xpath(r"div/div[3]/div/div/div[1]")
        nameStr = nameElement.text #image名称
        # //div[@id='searchResults']/div/a/div/div[2]/div[3]/div[2]/span[1]
        try:
            starElement = itemElement.find_element_by_xpath(r"div/div[2]/div[3]/div[2]/span[1]")

        except:
            starElement = itemElement.find_element_by_xpath(r"div/div[2]/div[3]/div/span[1]")
        starStr = starElement.text  # image star
        dockerPullCmd,versionList = dealitemElement(itemElement,nameStr) # image pull command , version dockerfile link list
        imageDict = {"nameStr":nameStr,"starStr":starStr,"dockerPullCmd":dockerPullCmd,"versionList":versionList}
        print(imageDict)
        imageList.append(imageDict)
    SaveOnePageDataToCsv(imageList)

    browser.quit()

def SaveOnePageDataToCsv(imageList):
    for imageDict in imageList:
        printCsvImage("docker_hub",imageDict)

def printCsvTitle(filename):
    path = "./csv/"
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    with open("./csv/"+filename+".csv",'w',newline='',encoding='utf8') as f:
        row_title = ['name','star','pull command','version','dockerfilelink']
        write=csv.writer(f)
        write.writerow(row_title)

def printCsvImage(filename,imageDict):
    # 不存在路径，创建路径
    path = "./csv/"
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    # 不存在文件则创建文件，添加文件头
    path = "./csv/" + filename + ".csv"
    isExists = os.path.exists(path)
    if not isExists:
        printCsvTitle(filename)

    if imageDict['versionList'] == None:
        with open("./csv/" + filename + ".csv", 'a', newline='', encoding='utf8') as f:
            row = [imageDict['nameStr'], imageDict['starStr'], imageDict['dockerPullCmd'],"",""]
            write = csv.writer(f)
            write.writerow(row)
    else:
        for version in imageDict['versionList']:
            with open("./csv/" + filename + ".csv", 'a', newline='', encoding='utf8') as f:
                row = [imageDict['nameStr'], imageDict['starStr'], imageDict['dockerPullCmd'],version['version'],version['link']]
                write = csv.writer(f)
                write.writerow(row)



def dealitemElement(itemElement,nameStr):
    imagePageUrl = itemElement.get_attribute("href")
    js = f'window.open("{imagePageUrl}");'
    browser.execute_script(js)

    browser.implicitly_wait(20)  # 智能等待20秒

    originHandle = browser.current_window_handle
    handles = browser.window_handles
    imageHandle = None
    for handle in handles:
        if handle != originHandle:
            imageHandle = handle

    browser.switch_to.window(imageHandle)
    try:
        dockerPullCmd = browser.find_element_by_xpath(r"/html/body/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[2]/input")\
            .get_attribute("value")
    except:
        dockerPullCmd = None
    try:
        versionUlElement = browser.find_element_by_xpath(
        r"/html/body/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[1]/div/div/div/div/div/ul[2]")
        versionList = getVersionAndDockerfileLink(versionUlElement)
    except:
        versionList = None
    browser.close()
    return dockerPullCmd,versionList

def getVersionAndDockerfileLink(versionUlElement):
    versionElements = versionUlElement.find_elements_by_xpath("li/a")
    versionList = []
    for versionElement in versionElements:
        dockerfileLinkStr = versionElement.get_attribute("href")
        version = versionElement.text
        versionList.append({"link" : dockerfileLinkStr, "version" : version})
    return versionList

if __name__ == '__main__':
    main()


