import xml.etree.ElementTree as ET
import hashlib
import base64
from typing import Dict, Any, Optional

class VFSParser:
    def __init__(self):
        self.vfs_data: Dict[str, Any] = {}
        self.vfs_name: Optional[str] = None
        self.current_path: List[str] = ["root"]

    def load_vfs(self, xml_path: str) -> bool:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            self.vfs_name = root.attrib.get("name", "unnamed_vfs")
            self.vfs_data = self._parse_folder(root.find("folder"))

            return True
        except FileNotFounderror:
            print(f"error: {xml_path} is not found.")
            return False
        except ET.Parseerror:
            print(f"error: incorrect XML format in {xml_path}.")
            return False
        except Exception as e:
            print(f"error in loading VFS: {e}")
            return False

    def _parse_folder(self, folder_element: ET.Element) -> Dict[str, Any]:
        if folder_element is None:
            return {}

        folder_name = folder_element.attrib.get("name", "unnamed_folder")
        folder_data: Dict[str, Any] = {"files": {}, "folders": {}}

        for item in folder_element:
            if item.tag == "file":
                file_name = item.attrib.get("name", "unnamed_file")
                file_type = item.attrib.get("type", "text")
                content = item.find("content").text if item.find("content") is not None else ""

                if file_type == "binary":
                    folder_data["files"][file_name] = {
                        "type": "binary",
                        "content": base64.b64decode(content)
                    }
                else:
                    folder_data["files"][file_name] = {
                        "type": "text",
                        "content": base64.b64decode(content).decode("utf-8")
                    }
            elif item.tag == "folder":
                subfolder_data = self._parse_folder(item)
                folder_data["folders"][item.attrib.get("name", "unnamed_folder")] = subfolder_data

        return folder_data

    def vfs_ls(self) -> str:
        if not self.vfs_data:
            return "VFS is not loaded."

        current_node = self._get_current_node()

        files = list(current_node.get("files", {}).keys())
        folders = list(current_node.get("folders", {}).keys())

        result = []
        if folders:
            result.extend(f"  {folder}/" for folder in folders)
        if files:
            result.extend(f"  {file}" for file in files)

        return "\n".join(result) if result else "\n"

    def vfs_cd(self, path: str) -> bool:
        if not self.vfs_data:
            return False

        # Разбиваем путь на компоненты
        if path.startswith("/"):
            # Абсолютный путь: начинаем с корня
            components = path.split("/")[1:]
            current_node = self.vfs_data
        else:
            # Относительный путь: начинаем с текущей директории
            components = path.split("/")
            current_node = self._get_current_node()

        # Обрабатываем компоненты пути
        for component in components:
            if not component or component == ".":
                continue  # Пропускаем пустые компоненты и "."
            if component == "..":
                # Поднимаемся на уровень выше
                if len(self.current_path) > 1:
                    self.current_path.pop()
                current_node = self._get_current_node()
                continue

            # Проверяем, существует ли папка с именем component
            if component in current_node.get("folders", {}):
                current_node = current_node["folders"][component]
                self.current_path.append(component)
            else:
                print(f"Ошибка: папка '{component}' не найдена.")
                return False

        return True

    def vfs_rm(self, name: str, recursive: bool = False) -> bool:
        if not self.vfs_data:
            print("VFS is not loaded.")
            return False

        current_node = self._get_current_node()

        if name in current_node.get("files", {}):
            del current_node["files"][name]
            return True

        if name in current_node.get("folders", {}):
            if not recursive and current_node["folders"][name].get("folders", {}): # or current_node["folders"][name].get("files", {})
                print(f"Error: folder '{name}' is not empty. Use flag -r for recursive remove.")
                return False
            del current_node["folders"][name]
            return True

        print(f"Error: file or folder '{name}' is not found.")
        return False

    def vfs_info(self) -> str:
        if not self.vfs_data:
            return "VFS is not loaded."

        data_str = str(self.vfs_data).encode("utf-8")
        sha256_hash = hashlib.sha256(data_str).hexdigest()
        return f"Name: {self.vfs_name}\n SHA-256: {sha256_hash}"

    def vfs_save(self, save_path: str) -> bool:
        try:
            root = ET.Element("vfs", name=self.vfs_name)
            root.append(self._build_folder_element(self.vfs_data))

            tree = ET.ElementTree(root)
            tree.write(save_path, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            print(f"error when saving VFS: {e}")
            return False

    def _get_current_node(self) -> Dict[str, Any]:
        current_node = self.vfs_data
        for folder in self.current_path[1:]:  # Пропускаем "root"
            current_node = current_node["folders"][folder]
        return current_node

    def _build_folder_element(self, folder_data: Dict[str, Any]) -> ET.Element:
        folder_element = ET.Element("folder", name="root" if folder_data.get("name") == "root" else "folder")

        for file_name, file_info in folder_data.get("files", {}).items():
            file_element = ET.SubElement(folder_element, "file", name=file_name, type=file_info["type"])
            content_element = ET.SubElement(file_element, "content")

            if file_info["type"] == "binary":
                content_element.text = base64.b64encode(file_info["content"]).decode("utf-8")
            else:
                content_element.text = base64.b64encode(file_info["content"].encode("utf-8")).decode("utf-8")

        for folder_name, subfolder_data in folder_data.get("folders", {}).items():
            subfolder_element = ET.SubElement(folder_element, "folder", name=folder_name)
            subfolder_element.append(self._build_folder_element(subfolder_data))

        return folder_element
