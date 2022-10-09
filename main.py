#-*- coding: utf-8 -*-
import japanize_kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

from kivy.lang import Builder
from kivy.properties import StringProperty,ObjectProperty,BoundedNumericProperty,NumericProperty
import sql_func, movie_func, my_func
import glob
import numpy as np

# for path in glob.glob('widget/*.kv'):
#     Builder.load_file(path)
#     print(f'{path}を読み込みました')

dbname = 'db/ANNOTATION.db'
sql = sql_func.AnnotationDB(dbname)

class RecordButton(Button):
    value = NumericProperty()


class RootWidget(Widget):
    texture_main = ObjectProperty()
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_resize=self._on_window_resize)
        Window.bind(on_minimize=self._on_window_minimize)
        Window.bind(on_maximize=self._on_window_maximize)

        self.mode = 'all'
        self.mode_option2 = 0 # 0:frame毎にラベル番号を選択してラベル付け。1:ラベル番号を固定してmove buttonを押すと固定されたラベルがフレームにラベル付けされる。
        self.label_number = 0


        self.tables = {}
        # subjectsのテーブル用データを登録
        records = [[record[0],sql.GetValueByID('Movies',record[1],'name')[0],record[2]] for record in sql.GetAllValuesByTable('Subjects')]
        header_layout, table_layout = self.Import_Subjects_Gridlayout(records)
        self.tables['Subjects'] = {'header':header_layout, 'table':table_layout}

        # Moviesのテーブル用データの登録
        records = [[record[0],record[1],record[3]] for record in sql.GetAllValuesByTable('Movies')]
        header_layout, table_layout = self.Import_Movies_Gridlayout(records)
        self.tables['Movies'] = {'header':header_layout, 'table':table_layout}

        # Subjectsのテーブルの表示
        self.ids['scroll_header'].add_widget(self.tables['Subjects']['header'])
        self.ids['scroll_list'].add_widget(self.tables['Subjects']['table'])

        # LabelListの表示
        records = [[record[0],record[1]] for record in sql.GetAllValuesByTable('Labels')]
        header_layout, table_layout = self.Import_Labels_Gridlayout(records)
        self.tables['Labels'] = {'header':header_layout, 'table':table_layout}
        self.ids['label_list'].add_widget(self.tables['Labels']['table'])

        # テーブルの切り替えメニューの追加
        tables = sql.GetTables()
        table_menu_layout = self.Import_Table_Menu(tables)
        self.ids['table_menu'].add_widget(table_menu_layout)

        # self.ids['scroll_list'].scroll_y=0.5
        # 選択中のsubjectの管理
        self.subject_id = 0

        self.frame = 1

        subject_id = sql.GetFlagSubjectIDLogs()
        if subject_id != 0:
            self.subject_id = str(subject_id)
            self.Update_Subject_Id(self.subject_id)
            self.ids['main_frame_label'].text = f"frame: {self.frame}"



    def _on_window_resize(self, window, width, height):
        self.Update_List_Image()

    def _on_window_maximize(self,largs):
        print("on_maximize")
        self.Update_List_Image()

    def _on_window_minimize(self,largs):
        print("on_minimize")
        self.Update_List_Image()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.moveButtonClicked('prev')

        elif keycode[1] == 'd':
            self.moveButtonClicked('next')

        elif keycode[1] == 'q':
            self.labelModeSwitch()

        elif keycode[1] == '1':
            if self.mode_option2 == 0:
                self.labelButtonClicked(1)
            elif self.mode_option2 == 1:
                self.labelSwitch(1)

        elif keycode[1] == '2':
            if self.mode_option2 == 0:
                self.labelButtonClicked(2)
            elif self.mode_option2 == 1:
                self.labelSwitch(2)

        elif keycode[1] == '3':
            if self.mode_option2 == 0:
                self.labelButtonClicked(3)
            elif self.mode_option2 == 1:
                self.labelSwitch(3)

        elif keycode[1] == '4':
            if self.mode_option2 == 0:
                self.labelButtonClicked(4)
            elif self.mode_option2 == 1:
                self.labelSwitch(4)

        elif keycode[1] == '5':
            if self.mode_option2 == 0:
                self.labelButtonClicked(5)
            elif self.mode_option2 == 1:
                self.labelSwitch(5)

        elif keycode[1] == '6':
            if self.mode_option2 == 0:
                self.labelButtonClicked(6)
            elif self.mode_option2 == 1:
                self.labelSwitch(6)

        elif keycode[1] == '0': #
            self.labelSwitch(0)

        elif keycode[1] == '-': # mode_option2の変更
            self.mode_option2_Switch()

    def moveButtonClicked(self,move):
        if self.mode_option2 == 1:
            self.labelButtonClicked(self.label_number)
        elif self.mode_option2 == 0:
            self.label_number = 0
            records = [[record[0],record[1]] for record in sql.GetAllValuesByTable('Labels')]
            header_layout, table_layout = self.Import_Labels_Gridlayout(records)
            self.tables['Labels'] = {'header':header_layout, 'table':table_layout}
            self.ids['label_list'].clear_widgets()
            self.ids['label_list'].add_widget(self.tables['Labels']['table'])

        if move == 'prev':
            if self.frame > 1:
                self.frame -= 1
        elif move == 'next':
            if self.frame_end > self.frame:
                self.frame += 1
        self.Update_Main_Image(self.frame)
        sql.UpdateLogs(self.subject_id,self.frame)
        self.ids['subject_menu_frame'].text = str(self.frame)

        self.Update_Annotation_table()
        self.Update_List_Image()

        self.ids['main_frame_label'].text = f"frame: {self.frame}"

    def labelButtonClicked(self,label):
        self.label_number = label
        if label != 0:
            records = [[record[0],record[1]] for record in sql.GetAllValuesByTable('Labels')]
            header_layout, table_layout = self.Import_Labels_Gridlayout(records)
            self.tables['Labels'] = {'header':header_layout, 'table':table_layout}
            self.ids['label_list'].clear_widgets()
            self.ids['label_list'].add_widget(self.tables['Labels']['table'])

            if self.mode == 'all':
                sql.UpdateAnnotationsAll(self.subject_id,label,label,self.frame)
            elif self.mode == 'right':
                sql.UpdateAnnotationsRight(self.subject_id,label,self.frame)
            elif self.mode == 'left':
                sql.UpdateAnnotationsLeft(self.subject_id,label,self.frame)

        self.Update_Annotation_table()

    def labelModeSwitch(self):
        if self.mode == 'all':
            self.mode = 'right'
        elif self.mode == 'right':
            self.mode = 'left'
        elif self.mode == 'left':
            self.mode = 'all'
        self.ids['subject_menu_mode'].text = self.mode

    def mode_option2_Switch(self):
        if self.mode_option2 == 0:
            self.mode_option2 = 1
            self.ids['subject_menu_mode_option2'].text = '連続'
        elif self.mode_option2 == 1:
            self.mode_option2 = 0
            self.ids['subject_menu_mode_option2'].text = '単発'

    def labelSwitch(self,label_number):
        self.label_number = label_number

        records = [[record[0],record[1]] for record in sql.GetAllValuesByTable('Labels')]
        header_layout, table_layout = self.Import_Labels_Gridlayout(records)
        self.tables['Labels'] = {'header':header_layout, 'table':table_layout}
        self.ids['label_list'].clear_widgets()
        self.ids['label_list'].add_widget(self.tables['Labels']['table'])

    # Table MenuのGridLayoutを生成
    def Import_Table_Menu(self,tables):
        menu_layout = GridLayout(cols=len(tables))
        for table in tables:
            if not table in ['Labels','Logs']:
                button = Button(text=table)
                button.bind(on_press=self.Switch_Table)
                self.ids[table+'_menu'] = button
                if table == 'Annotations':
                    button.disabled=True
                menu_layout.add_widget(button)
        return menu_layout

    # Tableの切り替え
    def Switch_Table(self,button):
        self.ids['scroll_header'].clear_widgets()
        self.ids['scroll_list'].clear_widgets()
        self.ids['scroll_header'].add_widget(self.tables[button.text]['header'])
        self.ids['scroll_list'].add_widget(self.tables[button.text]['table'])

    # Label表のheader, tableのlayoutを生成
    def Import_Labels_Gridlayout(self,records):
        rows = len(records)
        # header
        header_layout = GridLayout(cols=2)
        for col_name in ['id','name']:
            header_layout.add_widget(Label(text=col_name))
        # tables
        table_layout = GridLayout(cols=2,rows=rows)
        for record in records:
            if record[0] == self.label_number:
                for value in record:
                    table_layout.add_widget(Label(text=str(value),color='green'))
            else:
                for value in record:
                    table_layout.add_widget(Label(text=str(value)))
        return header_layout, table_layout

    # Movie表のheader, tableのlayoutを生成
    def Import_Movies_Gridlayout(self,records,rows=30):
        cols = ['id','name','frame']
        # header
        header_layout = GridLayout(cols=len(cols))
        for col_name in cols:
            header_layout.add_widget(Label(text=col_name))
        # tables
        table_layout = GridLayout(cols=len(cols),rows=rows,size_hint_y=None,row_default_height=30, height=30*rows)
        for record in records:
            for value in record:
                table_layout.add_widget(Label(text=str(value)))
        for _ in range(rows-len(records)):
            for __ in cols:
                table_layout.add_widget(Label(text='-'))
        return header_layout, table_layout

    # Subject表のheader, tableのlayoutを生成
    def Import_Subjects_Gridlayout(self,records,rows=30):
        cols = ['id','name','number','accept']
        # header
        header_layout = GridLayout(cols=len(cols))
        for col in cols:
            header_layout.add_widget(Label(text=col))
        layout = GridLayout(cols=len(cols),rows=rows,size_hint_y=None,row_default_height=30, height=30*rows)
        for record in records:
            for value in record:
                layout.add_widget(Label(text=str(value)))
            button = RecordButton(value=record[0])
            button.bind(on_press=self.update_accept_subject_id)
            layout.add_widget(button)
        for _ in range(rows-len(records)):
            for __ in cols:
                layout.add_widget(Label(text='-'))
        return header_layout, layout

    # Annotation表のheader, tableのlayoutを生成
    def Import_Annotations_Gridlayout(self,records,rows=30):
        scope = 4
        rows = scope*2 + 1

        cols = ['frame','right_label','left_label']
        # header
        header_layout = GridLayout(cols=len(cols))
        for col_name in cols:
            header_layout.add_widget(Label(text=col_name))
        # tables
        table_layout = GridLayout(cols=len(cols),rows=rows,size_hint_y=None,row_default_height=30, height=30*rows)
        records = np.array(records)

        records_T = records.T
        if len(records_T)!=0:
            if self.frame in records_T[0]:
                records2 = records[records_T[0] == self.frame]
            else:
                records2 = np.array([[self.frame,'-','-']])

            i = self.frame
            for _ in np.arange(scope):
                i -= 1
                if i in records_T[0]:
                        records2 = np.concatenate([records[records_T[0] == i], records2])
                else:
                    if i > 0:
                        records2 = np.concatenate([np.array([[i,'-','-']]),records2])
                    else:
                        records2 = np.concatenate([np.array([['-','-','-']]),records2])

            i = self.frame
            for _ in np.arange(scope):
                i += 1
                if i in records_T[0]:
                    records2 = np.concatenate([records2,records[records_T[0] == i]])
                else:
                    records2 = np.concatenate([records2,np.array([[i,'-','-']])])
        else:
            records2 = np.array([[self.frame,'-','-']])
            i = self.frame
            for _ in np.arange(scope):
                i -= 1
                if i > 0:
                    records2 = np.concatenate([np.array([[i,'-','-']]),records2])
                else:
                    records2 = np.concatenate([np.array([['-','-','-']]),records2])
            i = self.frame
            for _ in np.arange(scope):
                i += 1
                if i in records_T[0]:
                    records2 = np.concatenate([records2,records[records_T[0] == i]])
                else:
                    records2 = np.concatenate([records2,np.array([[i,'-','-']])])

        records = records2
        for record in records:
            for value in record:
                if (record[0] == self.frame)or(record[0] == str(self.frame)):
                    table_layout.add_widget(Label(text=str(value),color='red'))
                else:
                    table_layout.add_widget(Label(text=str(value)))
        # for _ in range(rows-len(records)):
        #     for __ in cols:
        #         table_layout.add_widget(Label(text='-'))
        return header_layout, table_layout

    # Subjectsボタンから選択されたとき
    def update_accept_subject_id(self,button):
        self.Update_Subject_Id(str(button.value))

    def Update_Subject_Id(self, subject_id):
        self.ids['subject_menu_label_id'].text = self.subject_id = subject_id
        self.ids['Annotations_menu'].disabled = False

        self.SubjectMovie = movie_func.Movie(sql.GetValueByID('Subjects',self.subject_id,'path')[0])

        # ImageMainWidgetに画像を表示
        records = sql.GetRecordsByValue("Logs","subject_id",self.subject_id)
        if records:
            self.frame = records[0][2]
        else:
            self.frame = 1
            sql.UpdateLogs(self.subject_id,self.frame)
        self.Update_Main_Image(self.frame)

        sql.UpdateLogsFlag(self.subject_id)

        # Annotaionsのテーブル用データの登録
        self.Update_Annotation_table()

        # Subjectの最後のフレーム番号を取得
        records = sql.GetRecordsByValue("Subjects","id",self.subject_id)
        self.frame_end = self.SubjectMovie.frame_count
        self.ids['subject_menu_frame'].text = str(self.frame)
        self.ids['subject_menu_frame_end'].text = str(int(self.frame_end))

        self.Update_List_Image()

    def Update_Annotation_table(self):
        # Annotaionsのテーブル用データの登録
        records,flag = sql.GetAnnotationsBySubjectID(self.subject_id)
        records = [[record[4],record[2],record[3]] for record in records]
        header_layout, table_layout = self.Import_Annotations_Gridlayout(records)
        self.tables['Annotations'] = {'header':header_layout, 'table':table_layout}

        self.ids['scroll_header'].clear_widgets()
        self.ids['scroll_list'].clear_widgets()
        self.ids['scroll_header'].add_widget(self.tables['Annotations']['header'])
        self.ids['scroll_list'].add_widget(self.tables['Annotations']['table'])
        # self.ids['scroll_list'].scroll_y = 0.5

    def Update_Main_Image(self,frame):
        ret, img = self.SubjectMovie.Get_Image(frame)
        if ret:
            texture = my_func.Img_To_Texture(img)
            self.texture_main = texture
        else:
            self.texture_main = None

    def Update_List_Image(self):
        scope = 2
        img_list = []

        frame = self.frame - scope
        for i in reversed(range(len(self.ids['image_list_grid'].children))):
            # print(i,self.ids['image_list_grid'].children[i].pos,self.ids['image_list_grid'].children[i].size)

            ret, img = self.SubjectMovie.Get_Image(frame)
            if ret:
                texture = my_func.Img_To_Texture(img)

            (h,w,_)=img.shape
            size=img.shape,self.ids['image_list_grid'].children[i].size
            size[1][1] = size[1][0]*h/w
            self.ids['image_list_grid'].children[i].canvas.clear()
            with self.ids['image_list_grid'].children[i].canvas:
                Rectangle(texture=texture,pos=self.ids['image_list_grid'].children[i].pos,size=self.ids['image_list_grid'].children[i].size)

            self.ids['image_list_grid'].children[i].clear_widgets()
            labels = sql.GetAnnotationsRecord(self.subject_id,frame)
            
            label_widget = Label(text=str(labels[0]),color='red',valign='bottom',halign='left',text_size=(10,40))
            self.ids['image_list_grid'].children[i].add_widget(label_widget)
            label_widget = Label(text=str(frame),color='red')
            self.ids['image_list_grid'].children[i].add_widget(label_widget)
            label_widget = Label(text=str(labels[1]),color='red',valign='bottom',halign='right',text_size=(10,40))
            self.ids['image_list_grid'].children[i].add_widget(label_widget)

            frame += 1

class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp,self).__init__(**kwargs)
        self.title = "Annotation"

    def build(self):
        return RootWidget()

if __name__=='__main__':
    MainApp().run()
