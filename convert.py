"""
Create separate quizzes that don't have entire
question banks attached to them.
"""

# to run, navigate to folder with convert.py and backup_folder, then run python convert.py

import os
from xml.dom import minidom
import io
from shutil import copytree, copyfile, ignore_patterns

backup_folder = './elfe_backups'
converted_folder = './converted_elfe_backups'
if not os.path.exists(converted_folder):
    os.mkdir(converted_folder)
for course_folder in os.listdir(backup_folder):
    if course_folder[0] != '.':
        rootdir = backup_folder+'/'+course_folder
        new_course_folder = course_folder.replace('backup-moodle2-course-','')
        new_path = converted_folder+'/'+new_course_folder
        if not os.path.exists(new_path):
            os.mkdir(new_path)

        # create dom from question bank
        question_path = rootdir + '/questions.xml'
        question_xml = minidom.parse(question_path)
        categories = question_xml.getElementsByTagName('question_category')

        # loop through all quizzes in the course
        for filename in os.listdir(rootdir+'/activities'):
            if filename[:4] == 'quiz':
                quiz_folder = rootdir + '/activities/' + filename
        
                # get quiz.xml file and title
                xml_path = quiz_folder + '/quiz.xml'
                quiz_xml = minidom.parse(xml_path)
                title = quiz_xml.getElementsByTagName('name')[0].firstChild.data
                title = title.replace('/','')
                topic_name = title[title.index(' - ')+3:]
                tense = title[0:title.index(' ')]
                moduleid = filename[5:]
    
                # create file structure
                backup_filename = 'backup-moodle2-activity-'+moduleid+'-'+filename+'-20151111-1406-nu'
                new_quiz_folder = new_path + '/' + title
                if not os.path.exists(new_quiz_folder):
                    os.mkdir(new_quiz_folder)
                else:
                    new_quiz_folder = new_quiz_folder+' 2'
                    os.mkdir(new_quiz_folder)
                new_quiz_activities = new_quiz_folder + '/activities'
                if not os.path.exists(new_quiz_activities):
                    os.mkdir(new_quiz_activities)
                new_quiz = new_quiz_activities + '/' + filename
        
                # copy all files from quiz folder
                if not os.path.exists(new_quiz):
                    copytree(quiz_folder, new_quiz)
            
            
                quiz_id = filename[5:]
        
                # copy over necessary files
                files_to_copy = ['files.xml','groups.xml','outcomes.xml','roles.xml','scales.xml']
                for needed_file in files_to_copy:
                    old_file_path = rootdir + '/' + needed_file
                    new_file_path = new_quiz_folder + '/' + needed_file
                    copyfile(old_file_path, new_file_path)
                backup_log = io.open(new_quiz_folder+'/moodle_backup.log','w')
                backup_log.close()
                calendar = io.open(new_quiz+'/calendar.xml','wb')
                calendar.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<events>\n</events>")
                calendar.close()
                filters = io.open(new_quiz+'/filters.xml','wb')
                filters.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<filters>\n\s<filter_actives>\n\s\
                    </filter_actives>\n\s<filter_configs>\n\s</filter_configs>\n</filters>")
                filters.close()
        
        
                # create dom from original moodle_backup
                backup_path = rootdir + '/moodle_backup.xml'
                backup_xml = minidom.parse(backup_path)
        
                # create dom from template quiz moodle_backup
                template_path = './moodle_backup_template.xml'
                backup_template = minidom.parse(template_path)
        
                # create file for new moodle_backup
                new_backup_path = new_quiz_folder + '/moodle_backup.xml'
                new_backup = io.open(new_backup_path,'w',encoding='utf8')
        
                # take basic information from original course backup
                information_node = backup_xml.firstChild.childNodes[1]
                information_children = information_node.childNodes
                node_to_remove = information_children[-1]
                # necessary intro information is up to original system context id
                while node_to_remove.nodeName != 'original_system_contextid':
                    information_node.removeChild(node_to_remove)
                    node_to_remove.unlink()
                    node_to_remove = information_children[-1]
                name_node = information_children[1]
                info_name = backup_xml.createTextNode(backup_filename+'.mbz')
                name_node.replaceChild(info_name,name_node.firstChild)
        
                # take quiz settings from template
                template_info = backup_template.firstChild.childNodes[1]
                template_activity = template_info.childNodes[3].childNodes[1].childNodes[1]
                template_moduleid = template_activity.childNodes[1]
                new_moduleid = backup_template.createTextNode(moduleid)
                template_moduleid.replaceChild(new_moduleid,template_moduleid.firstChild)
        
                template_title = template_activity.childNodes[7]
                new_title = backup_template.createTextNode(title)
                template_title.replaceChild(new_title,template_title.firstChild)
        
                template_dir = template_activity.childNodes[9]
                new_dir = backup_template.createTextNode('activities/'+filename)
                template_dir.replaceChild(new_dir, template_dir.firstChild)
        
                template_file = template_info.childNodes[5].childNodes[1].childNodes[5]
                new_filepath = backup_template.createTextNode(backup_filename+'.mbz')
                template_file.replaceChild(new_filepath,template_file.firstChild)
        
                template_inc_act = template_info.childNodes[5].childNodes[29].childNodes[3]
                new_inc_file = backup_template.createTextNode(filename)
                template_inc_act.replaceChild(new_inc_file,template_inc_act.firstChild)
                template_inc_val = template_info.childNodes[5].childNodes[29].childNodes[5]
                new_inc = backup_template.createTextNode(filename+'_included')
                template_inc_val.replaceChild(new_inc,template_inc_val.firstChild)
        
                template_user_act = template_info.childNodes[5].childNodes[31].childNodes[3]
                new_user_file = backup_template.createTextNode(filename)
                template_user_act.replaceChild(new_user_file,template_user_act.firstChild)
                template_user_val = template_info.childNodes[5].childNodes[31].childNodes[5]
                new_user = backup_template.createTextNode(filename+'_userinfo')
                template_user_val.replaceChild(new_user,template_user_val.firstChild)
        
        
                index = 1
                while index < len(template_info.childNodes):
                    information_node.appendChild(template_info.childNodes[index])
            
                new_backup.write(unicode(backup_xml.toxml(encoding="UTF-8"), errors='ignore'))
        
        
                # create new question.xml file
                new_question_path = new_quiz_folder + '/questions.xml'
                new_question = io.open(new_question_path,'w',encoding='utf8')
                new_question.write(u'<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
                new_question.write(u'<question_categories>\n')
        
                num_cat = 0
                for category in categories:
                    category_name = category.getElementsByTagName('name')[0].firstChild.data
                    category_topic = category_name[category_name.find(' - ')+3:]
                    category_tense = category_name[0:category_name.find(' ')]
                    if topic_name == category_topic and tense == category_tense:
                        new_question.write(category.toxml())
                        break
                new_question.write(u'\n</question_categories>')
                new_question.close()