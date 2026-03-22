import pandas as pd
import os
from DrissionPage import Chromium
##################################################
#########定义函数，传入url进入知乎问题的主页，并返回提问的全文以及tab
def search_keys(url):
    print('启动Chrome')
    browser=Chromium()
    tab=browser.latest_tab
    tab.get(url)
    quest_title=tab.ele('x://h1[@class="QuestionHeader-title"]').text
    all=tab.ele('x://a[@class="QuestionMainAction ViewAll-QuestionMainAction"]')
    if all:
        all.click()
    return quest_title,tab
#################################################
#########定义文件夹创建函数，传入主文件路径以及新建文件夹名称，并返回新创建文件夹的路径
def create_folder(folder_name,quest_title):
    folder_path=os.path.join(folder_name,quest_title)
    os.makedirs(folder_path,exist_ok=True)
    return folder_path
####################################################
######################定义滚动函数，防止知乎反爬
def scroll_to_load_all(tab):
    print("开始智能向下滚动加载...")
    previous_count = 0
    retry_count = 0
    max_retries = 3  # 如果连续 3 次滚动都没有新内容，说明到底了
    
    while True:
        # 1. 获取当前页面上已经加载的回答数量
        current_answers = tab.eles('x://div[@class="ContentItem AnswerItem"]')
        current_count = len(current_answers)
        
        # 2. 判断是否有新内容加载出来
        if current_count > previous_count:
            print(f"成功加载，当前回答总数: {current_count}")
            previous_count = current_count
            retry_count = 0  # 重新清零重试次数
        else:
            retry_count += 1
            print(f"未检测到新内容，正在重试 ({retry_count}/{max_retries})...")
            if retry_count >= max_retries:
                print("已滚动到页面最底部或无新回答，停止滚动。")
                break
                
        # 3. 核心魔法：拉扯式滚动法
        # 先滚到最底下
        tab.scroll.to_bottom()
        tab.wait(1) 
        
        # 然后往上回滚一点点（模拟你手动向上滑，重新触发加载事件）
        tab.scroll.up(500) 
        tab.wait(0.5)
        
        # 再滚回最底下
        tab.scroll.to_bottom()
        
        # 给服务器一点时间返回数据并渲染到页面上
        tab.wait(2) 

    return tab,current_answers

##########################################
###############定义回答下载函数，传入tab，元素列表以及文件夹路径，并返回list结果
def download_book(tab,current_answers,folder_path):
    answer_list=[]
    
    for anwser in current_answers:
        anwser_text=''
        writer=anwser.ele('x://span[@class="UserLink AuthorInfo-name"]/div/a[@class="UserLink-link"]').text.replace('\n','')
        anwser_content=anwser.ele('x://span[@itemprop="text"]')
        for row in anwser_content.children():
            if row.tag=="figure":
                row_src=row.ele('tag:img').attr("data-actualsrc")
                md_picture=f"![picture]({row_src})"

                anwser_text+=md_picture
            elif row.tag=="p":
                row_text=row.text
                anwser_text+=row_text
        row={'writer':writer,"anwser":anwser_text}
        answer_list.append(row)
        filename=folder_path+'/'+writer+".md"
        with open(filename,'w',encoding='utf-8') as f:
            f.write(anwser_text)
        print('所有回答原文已经为你保存为markdown')
    return answer_list
########################################
##########定义excel导出函数，传入要导出的列表，以及文件夹的位置
def save_to_excel(answer_list,folder_path):
    data=pd.DataFrame(answer_list)
    excel_name=folder_path+'/'+"data.xlsx"
    data.to_excel(excel_name,index=False)
    print(f'{excel_name}已经为你导出为excel格式')
############################################
###########################主函数   
def main():
    url=input("请输入问题的网址：")
    quest_title,tab=search_keys(url)
    folder_name=input('请填写文件夹绝对路径：')
    folder_path=create_folder(folder_name,quest_title)
    print(f'文件夹{folder_path}已经为你创建')
    tab,current_answers=scroll_to_load_all(tab)
    answer_list=download_book(tab,current_answers,folder_path)
    save_to_excel(answer_list, folder_path)
    
if __name__=="__main__":
    main()
    
    
    
        
        
    

