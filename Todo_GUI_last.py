
import flet as ft
from Todo_storage import load_tasks, save_tasks

def main(page: ft.Page):
    #入力部品
    page.title = "Forge Todo"

    title_input = ft.TextField(label="タイトル")
    title_error = ft.Text(
        "タイトルを入力してください",
        color=ft.Colors.RED,
        visible=False,
    )
    content_input = ft.TextField(label="内容", multiline=True)
    page.scroll = ft.ScrollMode.AUTO
    
    #ボタン部分
    # まだadd_taskが定義されていないため、イベントなしで作る
    submit_button = ft.ElevatedButton("追加")

    cancel_button = ft.TextButton(
        "キャンセル",
        visible=False,
    )
    #タスクの読み込み
    tasks = load_tasks()
    editing_task_id = [None]

    incomplete_task_list = ft.Column()
    completed_task_list = ft.Column(visible=False)

    # 既存タスクにIDを追加
    data_changed = False

    max_id = max(
            (task["id"] for task in tasks if "id" in task),
            default=0,
            )

    for task in tasks:
        if "id" not in task:
            max_id += 1
            task["id"] = max_id
            data_changed = True

    if data_changed:
        save_tasks(tasks)

    def check_title():
        title_text = title_input.value.strip()

        if title_text == "":
            title_error.visible = True
            page.update()
            return False

        title_error.visible = False
        page.update()
        return True

    def toggle_complete(e):
        task_id = e.control.data

        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = e.control.value
                break
        save_tasks(tasks)
        refresh_task_list()

    deleting_task_id = [None]
    #削除タスク
    def start_delete(e):
        task_id = e.control.data
        deleting_task_id[0] = task_id
        refresh_task_list()
        
    def cancel_delete(e):
        deleting_task_id[0] = None
        refresh_task_list()
        
    
    def confirm_delete(e):
        task_id = deleting_task_id[0]

        if task_id is None:
            return

        for task in tasks:
            if task["id"] == task_id:
                tasks.remove(task)
                break

        if editing_task_id[0] == task_id:
            finish_edit()

        deleting_task_id[0] = None
        save_tasks(tasks)
        refresh_task_list()
    #編集状態
    def start_edit(e):
        task_id = e.control.data

        for task in tasks:
            if task["id"] == task_id:
                title_input.value = task["title"]
                content_input.value = task["content"]
                editing_task_id[0] = task_id

                submit_button.text = "更新"
                submit_button.on_click = update_task
                cancel_button.visible = True
                page.update()
                return

    def update_task(e):
        if not check_title():
            return
        task_id = editing_task_id[0]
        new_title = title_input.value.strip()
        new_content = content_input.value.strip()
        for task in tasks:
            if task["id"] == task_id:
                task["title"] = new_title
                task["content"] = new_content
                break

        save_tasks(tasks)
        finish_edit()
        refresh_task_list()

    def finish_edit(e=None):
        editing_task_id[0] = None
        title_input.value = ""
        content_input.value = ""
        title_error.visible = False
        submit_button.text = "追加"
        submit_button.on_click = add_task
        cancel_button.visible = False
        page.update()

#タスク追加
    def add_task(e):
        if not check_title():
            return
        title_text = title_input.value.strip()
        content_text = content_input.value.strip()
        if tasks:
            new_id = max(task.get("id", 0) for task in tasks) + 1
        else:
            new_id = 1
        tasks.append(
            {
                "id": new_id,
                "title": title_text,
                "content": content_text,
                "completed": False,
            }
        )
        save_tasks(tasks)
        title_input.value = ""
        content_input.value = ""
        refresh_task_list()

    #タスクリスト更新
    def refresh_task_list():
        incomplete_task_list.controls.clear()
        completed_task_list.controls.clear()
        #ボタンと関数の接続、未完了と完了欄を空にする
        for task in tasks:
            is_deleting = task["id"] == deleting_task_id[0]
            #タスクを一件ずつ取り出す
            task_card = ft.Card(
                #タスクカード作成
                content=ft.Column(
                    [
                        ft.Checkbox(
                            label=task["title"],
                            value=task.get("completed", False),
                            data=task["id"],
                            on_change=toggle_complete,
                        ),
                        ft.Text(task["content"]),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                data=task["id"],
                                on_click=start_edit,
                                visible=not is_deleting,
                            ),

                            # 通常時のゴミ箱
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                data=task["id"],
                                on_click=start_delete,
                                visible=not is_deleting,
                            ),

                            # 削除確認中だけ表示
                            ft.Text(
                                "削除しますか？",
                                color=ft.Colors.RED,
                                visible=is_deleting,
                            ),

                            ft.TextButton(
                                "削除",
                                on_click=confirm_delete,
                                visible=is_deleting,
                            ),

                            ft.TextButton(
                                "キャンセル",
                                on_click=cancel_delete,
                                visible=is_deleting,
                            ),
                            ]
                            ),
                    ]
                )
            )

            if task.get("completed", False):
                #追加先を決める
                completed_task_list.controls.append(task_card)
            else:
                incomplete_task_list.controls.append(task_card)
        #画面更新
        page.update()

    def complete_button(e):
        completed_task_list.visible = not completed_task_list.visible
        if completed_task_list.visible :
            e.control.icon = ft.Icons.KEYBOARD_ARROW_DOWN
        else:
            e.control.icon = ft.Icons.KEYBOARD_ARROW_RIGHT

        page.update()

    # 全関数の定義後にイベントを接続
    submit_button.on_click = add_task
    cancel_button.on_click = finish_edit

    page.add(
        ft.Text("Forge Todo", size=30),
        title_input,
        title_error,
        content_input,
        ft.Divider(),
        ft.Row(
        [
        submit_button,
        cancel_button,
        ]
        ),
        ft.Container(
            content=incomplete_task_list,
            expand=True,
        ),
        ft.Divider(),
        ft.Row([
        ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
            on_click=complete_button,
        ),
        ft.Text("完了タスク", size=15),
        ]
        ),
        ft.Container(
            content=completed_task_list,
        )
    )    

    refresh_task_list()


ft.run(main)
