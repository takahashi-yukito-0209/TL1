import bpy
import math
import bpy_extras

# blenderに登録するアドオン情報 
bl_info = {
    "name": "レベルエディタ",
    "author": "kamata",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


# アドオン有効化時コールバック
def register():
    # Blenderにクラスを登録
    for addon_class in classes:
        bpy.utils.register_class(addon_class)

    # メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")


# アドオン無効化時コールバック
def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    # Blenderからクラスを削除
    for addon_class in classes:
        bpy.utils.unregister_class(addon_class)

    print("レベルエディタが無効化されました。")


# メニュー項目描画
def draw_menu_manual(self, context):
    # self : 呼び出し元のクラスインスタンス。C++でいうthisポインタ
    # context : カーソルを合わせたときのポップアップのカスタマイズなどに使用

    # トップバーの「エディターメニュー」に項目（オペレータ）を追加
    self.layout.operator("wm.url_open_perset", text="Manual", icon='HELP')


# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"

    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"

    # 著者表示用の文字列
    bl_description = "拡張メニュー by " + bl_info["author"]

    # サブメニューの描画
    def draw(self, context):
        # トップバーの「エディターメニュー」に項目（オペレータ）を追加
        self.layout.operator(
            MYADDON_OT_stretch_vertex.bl_idname,
            text=MYADDON_OT_stretch_vertex.bl_label
        )

        self.layout.operator(
            MYADDON_OT_create_ico_sphere.bl_idname,
            text=MYADDON_OT_create_ico_sphere.bl_label
        )

        self.layout.operator(
            MYADDON_OT_export_scene.bl_idname,
            text=MYADDON_OT_export_scene.bl_label
        )

    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# オペレータ 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"

    # リドゥ、アンドゥ可能オプション
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれるコールバック関数
    def execute(self, context):
        """Cubeの先頭頂点をX方向へ移動する"""

        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました。")

        # オペレータの命令終了を通知
        return {'FINISHED'}


# オペレータ ICO球生成
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        """ICO球を生成する"""

        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を生成しました。")

        return {'FINISHED'}


# オペレータ シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    bl_options = {'REGISTER', 'UNDO'}

    # 出力するファイルの拡張子
    filename_ext = ".scene"

    def write_and_print(self, output_file, text):
        """コンソールとファイルに同じ文字列を出力する"""

        print(text)
        output_file.write(text)
        output_file.write('\n')

    def parse_scene_recursive(self, output_file, scene_object, hierarchy_level):
        """オブジェクト1個分の情報を出力し、子オブジェクトを再帰的に処理する"""

        # 階層の深さに応じてインデントを作成
        indent_text = ''
        for hierarchy_index in range(hierarchy_level):
            indent_text += '\t'

        # オブジェクト種別を出力
        self.write_and_print(output_file, indent_text + scene_object.type)

        # オブジェクト名を出力
        self.write_and_print(output_file, indent_text + "N %s" % scene_object.name)

        # ローカルトランスフォームを分解
        translation, rotation, scale = scene_object.matrix_local.decompose()

        # クォータニオンからオイラー角へ変換
        rotation = rotation.to_euler()

        # ラジアンから度数法へ変換
        rotation.x = math.degrees(rotation.x)
        rotation.y = math.degrees(rotation.y)
        rotation.z = math.degrees(rotation.z)

        # トランスフォーム情報を出力
        self.write_and_print(
            output_file,
            indent_text + "T %f %f %f" % (translation.x, translation.y, translation.z)
        )

        self.write_and_print(
            output_file,
            indent_text + "R %f %f %f" % (rotation.x, rotation.y, rotation.z)
        )

        self.write_and_print(
            output_file,
            indent_text + "S %f %f %f" % (scale.x, scale.y, scale.z)
        )

        # file_nameカスタムプロパティがある場合だけ出力
        if "file_name" in scene_object:
            self.write_and_print(
                output_file,
                indent_text + "N %s" % scene_object["file_name"]
            )

        # オブジェクト情報の終端を出力
        self.write_and_print(output_file, indent_text + "END")

        # オブジェクトごとの区切り
        self.write_and_print(output_file, "")

        # 子オブジェクトを再帰的に処理
        for child_object in scene_object.children:
            self.parse_scene_recursive(
                output_file,
                child_object,
                hierarchy_level + 1
            )

    def export(self):
        """シーン内のオブジェクト情報をファイルに出力する"""

        print("シーン情報出力開始… %r" % self.filepath)

        # ファイルをテキスト形式で書き出し用にオープン
        with open(self.filepath, "wt") as output_file:

            # シーン開始文字列を書き込み
            self.write_and_print(output_file, "SCENE")

            # シーン内の全オブジェクトを走査
            for scene_object in bpy.context.scene.objects:

                # 親オブジェクトがある場合は、再帰処理側で出力するためスキップ
                if scene_object.parent:
                    continue

                # ルート直下のオブジェクトから再帰的に出力
                self.parse_scene_recursive(output_file, scene_object, 0)

    def execute(self, context):
        """シーン出力処理を実行する"""

        print("シーン情報をExportします")

        # ファイルに出力
        self.export()

        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}


# オペレータ file_nameカスタムプロパティ追加
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName 追加"
    bl_description = "file_nameカスタムプロパティを追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """選択中オブジェクトにfile_nameカスタムプロパティを追加する"""

        # 選択中のオブジェクト
        selected_object = context.object

        # オブジェクトが未選択なら処理しない
        if selected_object is None:
            return {'CANCELLED'}

        # file_nameカスタムプロパティを追加
        selected_object["file_name"] = ""

        return {'FINISHED'}


# パネル file_name
class OBJECT_PT_file_name(bpy.types.Panel):
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        """file_nameカスタムプロパティ用のUIを表示する"""

        # UIレイアウト
        layout = self.layout

        # 選択中のオブジェクト
        selected_object = context.object

        # オブジェクトが未選択なら表示しない
        if selected_object is None:
            return

        # file_nameが存在する場合は入力欄を表示
        if "file_name" in selected_object:
            layout.prop(
                selected_object,
                '["file_name"]',
                text=self.bl_label
            )

        # file_nameが存在しない場合は追加ボタンを表示
        else:
            layout.operator(MYADDON_OT_add_filename.bl_idname)


# Blenderに登録するクラスリスト
classes = (
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    MYADDON_OT_add_filename,
    OBJECT_PT_file_name,
    TOPBAR_MT_my_menu,
)


# テスト実行用コード
if __name__ == "__main__":
    register()