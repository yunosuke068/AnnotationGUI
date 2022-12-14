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
import glob, os
import numpy as np

# for path in glob.glob('widget/*.kv'):
#     Builder.load_file(path)
#     print(f'{path}を読み込みました')


movies_path = 'db/source'
# subjects_path = 'db/Subjects'
subjects_path = '..\FaceRecognition\split_movie'

dbname = 'db/ANNOTATION.db'
sql = sql_func.AnnotationDB(dbname)

# 適用ボタン用のボタンウィジェット
class RecordButton(Button):
    value = NumericProperty()

class RootWidget(Widget):
    texture_main = ObjectProperty()
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

        # /*******
        # イベント管理
        # *******/
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_resize=self._on_window_resize)
        Window.bind(on_minimize=self._on_window_minimize)
        Window.bind(on_maximize=self._on_window_maximize)

        # /*******
        # 変数
        # *******/
        self.mode_option1 = 'all' # all:両手、right:右手、left:左手にラベル付け
        self.mode_option2 = 0 # 0:単発、frame毎にラベル番号を選択してラベル付け。1:連続、ラベル番号を固定してmove buttonを押すと固定されたラベルがフレームにラベル付けされる。
        self.label_number = 0 # 選択されているラベル番号の管理
        self.frame = 1 # 現在のframeの管理

        # /**選択されているsubject_idの管理**/
        logs = sql.GetRecords('Logs',['id'],{'flag':1}) # 前回表示していたsubjctのid取得
        if len(logs) > 0:
            subject_id = logs[0]['id']
            if subject_id != 0: # 前回表示していたsubjectがある場合
                self.subject_id = str(subject_id)
        else:
            self.subject_id = 0


        # /*******
        # Subjects, Movies GridLayout用のリストを生成
        # *******/
        self.tables = {} # Subjects, MoviesのGridLayoutWidgetのheaderとtableをdictで管理

        # Subjects
        records = sql.GetRecords('Subjects',['id','name'],option={'sql_str':'LIMIT 30'})
        header_layout, table_layout = self.Get_Subjects_GridLayout_Widgets(records) # Subjects tableのGridLayoutWidgetを取得
        self.tables['Subjects'] = {'header':header_layout, 'table':table_layout}

        # Movies
        records = sql.GetRecords('Movies',['id','name','frame'])
        header_layout, table_layout = self.Get_Movies_GridLayout_Widgets(records) # Subjects tableのGridLayoutWidgetを取得
        self.tables['Movies'] = {'header':header_layout, 'table':table_layout}


        # /*******
        # アプリのビュー表示
        # *******/

        # TableMenuの表示
        tables = sql.GetTables()
        table_menu_layout = self.Get_Table_Menu_GridLayout_Widget(tables) # TableMenuのGridLayoutWidgetを取得
        self.ids['table_menu'].add_widget(table_menu_layout) # TableMenuのGridLayoutWidgetを表示

        # ScrollHeader, ScrollListの表示
        if self.subject_id != 0: # 前回表示していたsubjct_idがある場合
            self.Change_Subject(self.subject_id)
            self.ids['main_frame_label'].text = f"frame: {self.frame}"
        else: # 前回表示していたsubjct_idがない場合
            self.ids['scroll_header'].add_widget(self.tables['Subjects']['header'])
            self.ids['scroll_list'].add_widget(self.tables['Subjects']['table'])

        # LabelList widgetの更新
        self.Update_Label_List_Widget()


    # /*******
    # イベントメソッド
    # *******/

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a':
            self.Move_Button_Clicked('prev')

        elif keycode[1] == 'd':
            self.Move_Button_Clicked('next')

        elif keycode[1] == 'q':
            self.Mode_Option1_Switch()

        elif keycode[1] == '1':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(1)
            elif self.mode_option2 == 1:
                self.Label_Switch(1)

        elif keycode[1] == '2':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(2)
            elif self.mode_option2 == 1:
                self.Label_Switch(2)

        elif keycode[1] == '3':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(3)
            elif self.mode_option2 == 1:
                self.Label_Switch(3)

        elif keycode[1] == '4':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(4)
            elif self.mode_option2 == 1:
                self.Label_Switch(4)

        elif keycode[1] == '5':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(5)
            elif self.mode_option2 == 1:
                self.Label_Switch(5)

        elif keycode[1] == '6':
            if self.mode_option2 == 0:
                self.Label_Button_Clicked(6)
            elif self.mode_option2 == 1:
                self.Label_Switch(6)

        elif keycode[1] == '0': #
            self.Label_Switch(0)

        elif keycode[1] == '-': # mode_option2の変更
            self.Mode_Option2_Switch()

    # Windowのサイズを変更イベント
    def _on_window_resize(self, window, width, height):
        self.Update_Image_List_Widget()

    # Windowを最大化イベント
    def _on_window_maximize(self,largs):
        self.Update_Image_List_Widget()

    # Windowの最小化いイベント
    def _on_window_minimize(self,largs):
        self.Update_Image_List_Widget()


    # /*******
    # キーボードクリックメソッド
    # *******/

    # FrameのPrev、Nextキーのクリック
    def Move_Button_Clicked(self,move):
        if self.mode_option2 == 1: # 連続モード
            self.Label_Button_Clicked(self.label_number)
        elif self.mode_option2 == 0: # 単発モード
            self.label_number = 0
            self.Update_Label_List_Widget() # LabelList widgetの更新

        if move == 'prev':
            if self.frame > 1:
                self.frame -= 1
        elif move == 'next':
            if self.frame_end > self.frame:
                self.frame += 1
        self.Update_Image_Main_Widget(self.frame) # ImageMainWidgetの画像を現在frameの画像に更新

        # 現在、表示されているsubjectとframeをLogsに保存
        sql.UpdateRecords('Logs',{'subject_id':self.subject_id},{'frame':self.frame})

        self.ids['subject_menu_frame'].text = str(self.frame)

        self.Update_Annotation_Scroll_Widgets() # Annotation Tableを更新
        self.Update_Image_List_Widget() # Label Tableを更新

        self.ids['main_frame_label'].text = f"frame: {self.frame}"

    def Label_Button_Clicked(self,label):
        self.label_number = label
        if label != 0:
            self.Update_Label_List_Widget() # LabelList widgetの更新

            if self.mode_option1 == 'all':
                sql.UpdateRecords('Annotations',{'subject_id':self.subject_id,'frame':self.frame},{'subject_id':self.subject_id,'frame':self.frame,'right_label_id':label,'left_label_id':label})
            elif self.mode_option1 == 'right':
                sql.UpdateRecords('Annotations',{'subject_id':self.subject_id,'frame':self.frame},{'subject_id':self.subject_id,'frame':self.frame,'right_label_id':label})
            elif self.mode_option1 == 'left':
                sql.UpdateRecords('Annotations',{'subject_id':self.subject_id,'frame':self.frame},{'subject_id':self.subject_id,'frame':self.frame,'left_label_id':label})

        self.Update_Annotation_Scroll_Widgets()

    def Mode_Option1_Switch(self):
        if self.mode_option1 == 'all':
            self.mode_option1 = 'right'
        elif self.mode_option1 == 'right':
            self.mode_option1 = 'left'
        elif self.mode_option1 == 'left':
            self.mode_option1 = 'all'
        self.ids['subject_menu_mode'].text = self.mode_option1

    def Mode_Option2_Switch(self):
        if self.mode_option2 == 0:
            self.mode_option2 = 1
            self.ids['subject_menu_mode_option2'].text = '連続'
        elif self.mode_option2 == 1:
            self.mode_option2 = 0
            self.ids['subject_menu_mode_option2'].text = '単発'

    def Label_Switch(self,label_number):
        self.label_number = label_number
        self.Update_Label_List_Widget() # LabelList widgetの更新


    # /*******
    # アップ内ボタンのクリックメソッド
    # *******/

    # Tableの切り替え
    def Table_Menu_Button_Clicked(self,button):
        self.ids['scroll_header'].clear_widgets()
        self.ids['scroll_list'].clear_widgets()
        self.ids['scroll_header'].add_widget(self.tables[button.text]['header'])
        self.ids['scroll_list'].add_widget(self.tables[button.text]['table'])

    # Subjectsボタンから選択されたとき
    def Subject_List_Button_Clicked(self,button):
        self.Change_Subject(str(button.value))


    # /*******
    # データベースのテーブルからGridLayout生成メソッド
    # *******/

    # Table MenuのGridLayoutを生成
    def Get_Table_Menu_GridLayout_Widget(self,tables):
        menu_layout = GridLayout(cols=len(tables))
        for table in tables:
            if not table in ['Labels','Logs']:
                button = Button(text=table)
                button.bind(on_press=self.Table_Menu_Button_Clicked)
                self.ids[table+'_menu'] = button
                if table == 'Annotations':
                    button.disabled=True
                menu_layout.add_widget(button)
        return menu_layout

    # Label表のheader, tableのlayoutを生成
    def Get_Labels_GridLayout_Widgets(self,records):
        rows = len(records)
        cols = records[0].keys()
        # header
        header_layout = GridLayout(cols=len(cols))
        for col_name in cols:
            header_layout.add_widget(Label(text=col_name))
        # tables
        table_layout = GridLayout(cols=len(cols),rows=rows)
        for record in records:
            if record['id'] == self.label_number:
                for value in record.values():
                    table_layout.add_widget(Label(text=str(value),color='green'))
            else:
                for value in record.values():
                    table_layout.add_widget(Label(text=str(value)))
        return header_layout, table_layout

    # Movie表のheader, tableのlayoutを生成
    def Get_Movies_GridLayout_Widgets(self,records,rows=30):
        if len(records) > 0:
            cols = list(records[0].keys())
        else:
            cols = ['id']
        # header
        header_layout = GridLayout(cols=len(cols))
        for col_name in cols:
            header_layout.add_widget(Label(text=col_name))
        # tables
        table_layout = GridLayout(cols=len(cols),rows=rows,size_hint_y=None,row_default_height=30, height=30*rows)
        for record in records:
            for value in record.values():
                table_layout.add_widget(Label(text=str(value)))
        for _ in range(rows-len(records)):
            for __ in cols:
                table_layout.add_widget(Label(text='-'))
        return header_layout, table_layout

    # Subject表のheader, tableのlayoutを生成
    def Get_Subjects_GridLayout_Widgets(self,records,rows=30):
        if len(records) > 0:
            cols = list(records[0].keys())
        else:
            cols = ['id']
        cols.append('accept')
        # header
        header_layout = GridLayout(cols=len(cols)) # GridLayoutウィジェットのインスタンスを作成
        for col in cols:
            header_layout.add_widget(Label(text=col))
        layout = GridLayout(cols=len(cols),rows=rows,size_hint_y=None,row_default_height=30, height=30*rows)
        for record in records:
            for value in record.values():
                layout.add_widget(Label(text=str(value)))
            button = RecordButton(value=record['id'])
            button.bind(on_press=self.Subject_List_Button_Clicked)
            layout.add_widget(button)
        for _ in range(rows-len(records)):
            for __ in cols:
                layout.add_widget(Label(text='-'))
        return header_layout, layout

    # Annotation表のheader, tableのlayoutを生成
    def Get_Annotations_GridLayout_Widgets(self,records,rows=30):
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
                records2 = np.concatenate([records2,np.array([[i,'-','-']])])

        records = records2
        for record in records:
            for value in record:
                if (record[0] == self.frame)or(record[0] == str(self.frame)):
                    table_layout.add_widget(Label(text=str(value),color='red'))
                else:
                    table_layout.add_widget(Label(text=str(value)))

        return header_layout, table_layout

    # /*******
    # Widgetsの更新メソッド
    # *******/

    # AnnotationsのScroll_Header, Scroll_List Widgetsの更新
    def Update_Annotation_Scroll_Widgets(self):
        # Annotaionsのテーブル用データの登録
        records = sql.GetRecords('Annotations',['frame','right_label_id','left_label_id'],{'subject_id':self.subject_id},option={'sql_str':f'AND frame < {self.frame + 10} AND frame > {self.frame - 10} ORDER BY frame LIMIT 30'})
        records = [[record['frame'],record['right_label_id'],record['left_label_id']] for record in records]
        header_layout, table_layout = self.Get_Annotations_GridLayout_Widgets(records)
        self.tables['Annotations'] = {'header':header_layout, 'table':table_layout}

        self.ids['scroll_header'].clear_widgets()
        self.ids['scroll_list'].clear_widgets()
        self.ids['scroll_header'].add_widget(self.tables['Annotations']['header'])
        self.ids['scroll_list'].add_widget(self.tables['Annotations']['table'])
        # self.ids['scroll_list'].scroll_y = 0.5

    # Image_Main Widgetの更新
    def Update_Image_Main_Widget(self,frame):
        ret, img = self.SubjectMovie.Get_Image(frame)
        if ret:
            texture = my_func.Img_To_Texture(img)
            self.texture_main = texture
        else:
            self.texture_main = None

    # Image_List Widgetの更新
    def Update_Image_List_Widget(self):
        scope = 2
        img_list = []

        frame = self.frame - scope
        for i in reversed(range(len(self.ids['image_list_grid'].children))):
            print(i, self.ids['image_list_grid'].children[i].pos, self.ids['image_list_grid'].children[i].size)
            # /** 画像の表示 **/
            ret, img = self.SubjectMovie.Get_Image(frame)
            if ret:
                texture = my_func.Img_To_Texture(img)

            (h,w,_)=img.shape
            size=img.shape,self.ids['image_list_grid'].children[i].size
            size[1][1] = size[1][0]*h/w
            self.ids['image_list_grid'].children[i].canvas.clear()
            with self.ids['image_list_grid'].children[i].canvas:
                Rectangle(texture=texture,pos=self.ids['image_list_grid'].children[i].pos,size=self.ids['image_list_grid'].children[i].size)

            # /**ImageList widgetの画像にframe番号とlabel番号を表示**/
            self.ids['image_list_grid'].children[i].clear_widgets() # Label widgetを削除
            labels = sql.GetRecords('Annotations',['right_label_id','left_label_id'],{'subject_id':self.subject_id,'frame':frame},{'sql_str':'LIMIT 5'})
            if len(labels) == 0:
                label = {'right_label_id':'-','left_label_id':'-'}
            else:
                label = labels[0]
            label_widget = Label(text=str(label['left_label_id']),color='red',valign='bottom',halign='left',text_size=(10,40))
            self.ids['image_list_grid'].children[i].add_widget(label_widget)

            label_widget = Label(text=str(frame),color='red')
            self.ids['image_list_grid'].children[i].add_widget(label_widget)

            label_widget = Label(text=str(label['right_label_id']),color='red',valign='bottom',halign='right',text_size=(10,40))
            self.ids['image_list_grid'].children[i].add_widget(label_widget)

            frame += 1

    # LabelList Widgetの更新。self.label_numberの番号のラベルがハイライトされる。
    def Update_Label_List_Widget(self):
        records = sql.GetRecords('Labels',['id','name'])
        header_layout, table_layout = self.Get_Labels_GridLayout_Widgets(records)
        self.tables['Labels'] = {'header':header_layout, 'table':table_layout}
        self.ids['label_list'].clear_widgets()
        self.ids['label_list'].add_widget(self.tables['Labels']['table'])

    # /*******
    # メソッド
    # *******/

    # Subjectの変更
    def Change_Subject(self, subject_id):
        self.ids['subject_menu_label_id'].text = self.subject_id = subject_id
        self.ids['Annotations_menu'].disabled = False

        sr = sql.GetRecords('Subjects',['path'],{'id':subject_id})[0]
        self.SubjectMovie = movie_func.Movie(sr['path'])

        # ImageMainWidgetに画像を表示
        records = sql.GetRecords('Logs',['frame'],{'subject_id':self.subject_id},{'sql_str':'LIMIT 1'})
        if records:
            self.frame = records[0]['frame']
        else:
            self.frame = 1
            sql.UpdateRecords('Logs',{'subject_id':self.subject_id},{'subject_id':subject_id,'frame':self.frame})
        self.Update_Image_Main_Widget(self.frame)
        
        sql.cursor.execute("UPDATE Logs SET flag = 0")
        sql.UpdateRecords('Logs',{'subject_id':self.subject_id},{'subject_id':subject_id,'flag':1})

        # Annotaionsのテーブル用データの登録
        self.Update_Annotation_Scroll_Widgets()

        # Subjectの最後のフレーム番号を取得
        self.frame_end = self.SubjectMovie.frame_count
        self.ids['subject_menu_frame'].text = str(self.frame)
        self.ids['subject_menu_frame_end'].text = str(int(self.frame_end))

        self.Update_Image_List_Widget()

class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp,self).__init__(**kwargs)
        self.title = "Annotation"

        # sourceディレクトリのMovies動画をdbに読み込み
        for path in glob.glob(f'{movies_path}/*.mp4'):
            movie = movie_func.Movie(path)
            source_name = os.path.basename(movie.path).replace('.mp4','')
            sql.UpdateRecords('Movies',{'name':source_name},{'name':source_name,'fps':movie.fps,'frame':movie.frame_count,'path':path})

        # SubjectsディレクトリのSubjects動画をdbに読み込み
        for path in glob.glob(f'{subjects_path}/*.mp4'):
            movie = movie_func.Movie(path)
            filename = os.path.basename(movie.path).replace('.mp4','')
            [source_name, order_number] = filename.split('_')
            sql.UpdateRecords('Subjects',{'name':filename},{'name':filename,'fps':movie.fps,'frame':movie.frame_count,'path':path})

    def build(self):
        return RootWidget()

if __name__=='__main__':
    MainApp().run()
