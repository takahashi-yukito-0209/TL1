import bpy
import math
import bpy_extras
import gpu
import gpu_extras.batch
import copy

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


# コライダー描画
class DrawCollider:
    # 描画ハンドル
    draw_handler = None

    @staticmethod
    def draw_collider():
        """シーン内の全オブジェクトにコライダー用のワイヤーフレームを描画する"""

        # 頂点データ
        vertices = {"pos": []}

        # インデックスデータ
        indices = []

        # 立方体の各頂点へのオフセット
        offsets = [
            [-0.5, -0.5, -0.5],
            [+0.5, -0.5, -0.5],
            [-0.5, +0.5, -0.5],
            [+0.5, +0.5, -0.5],
            [-0.5, -0.5, +0.5],
            [+0.5, -0.5, +0.5],
            [-0.5, +0.5, +0.5],
            [+0.5, +0.5, +0.5],
        ]

        # 立方体のサイズ
        collider_size = [2, 2, 2]

        # シーン内の全オブジェクトを走査
        for scene_object in bpy.context.scene.objects:

            # このオブジェクトの開始頂点番号
            start_vertex_index = len(vertices["pos"])

            # Boxの8頂点分を追加
            for offset in offsets:

                # オブジェクト位置をコピー
                position = copy.copy(scene_object.location)

                # オフセットを加算して頂点座標を作成
                position[0] += offset[0] * collider_size[0]
                position[1] += offset[1] * collider_size[1]
                position[2] += offset[2] * collider_size[2]

                # 頂点データに追加
                vertices["pos"].append(position)

            # 前面
            indices.append([start_vertex_index + 0, start_vertex_index + 1])
            indices.append([start_vertex_index + 1, start_vertex_index + 3])
            indices.append([start_vertex_index + 3, start_vertex_index + 2])
            indices.append([start_vertex_index + 2, start_vertex_index + 0])

            # 奥面
            indices.append([start_vertex_index + 4, start_vertex_index + 5])
            indices.append([start_vertex_index + 5, start_vertex_index + 7])
            indices.append([start_vertex_index + 7, start_vertex_index + 6])
            indices.append([start_vertex_index + 6, start_vertex_index + 4])

            # 前面と奥面をつなぐ辺
            indices.append([start_vertex_index + 0, start_vertex_index + 4])
            indices.append([start_vertex_index + 1, start_vertex_index + 5])
            indices.append([start_vertex_index + 2, start_vertex_index + 6])
            indices.append([start_vertex_index + 3, start_vertex_index + 7])

        # ビルトインのシェーダを取得
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        # バッチを作成
        batch = gpu_extras.batch.batch_for_shader(
            shader,
            "LINES",
            vertices,
            indices=indices
        )

        # 色を指定
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)

        # 描画
        batch.draw(shader)


# アドオン有効化時コールバック
def register():
    # Blenderにクラスを登録
    for addon_class in classes:
        bpy.utils.register_class(addon_class)

    # メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)

    # 3Dビューに描画関数を登録
    DrawCollider.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        DrawCollider.draw_collider,
        (),
        "WINDOW",
        "POST_VIEW"
    )

    print("レベルエディタが有効化されました。")


# アドオン無効化時コールバック
def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    # 3Dビューから描画関数を解除
    if DrawCollider.draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            DrawCollider.draw_handler,
            "WINDOW"
        )
        DrawCollider.draw_handler = None

    # Blenderからクラスを削除
    for addon_class in classes:
        bpy.utils.unregister_class(addon_class)

    print("レベルエディタが無効化されました。")


# メニュー項目描画
def draw_menu_manual(self, context):
    # トップバーの「エディターメニュー」に項目（オペレータ）を追加
    self.layout.operator("wm.url_open_perset", text="Manual", icon='HELP')


# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        """トップバーの拡張メニューを描画する"""

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

    def submenu(self, context):
        """既存メニューへサブメニューを追加する"""

        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


# オペレータ 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Cubeの先頭頂点をX方向へ移動する"""

        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました。")

        return {'FINISHED'}


# オペレータ ICO球生成
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

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