import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageFile, ImageQt
import math
import face_recognition

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

__version__ = '0.3.0'

# 口罩图片的路径
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

itm = []  # 口罩的图片列表
itm_pos = []  # 口罩的位置
maxWidth = 0
maxWidthIndex = 0
selectedIndex = 2
selectedRect = 0
pic_path = ''
mask_path = os.path.join(IMAGE_DIR, "default-mask.png")
selectedFace = None
count=0

# 选择和显示人物图片和口罩图片的窗口
class maskWindow(QWidget):
    faceImageWithMask = None

    def __init__(self):
        super(maskWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(900, 600)
        self.setWindowTitle("为图片中的人物戴上口罩")
        # 左边人物和按钮
        self.person = QWidget(self)

        # 人物图片使用QGraphicsView
        self.person_pic = QtWidgets.QGraphicsView()
        self.scene = QGraphicsScene()  # 创建场景
        self.person_pic.setFixedSize(int(self.width() * 2 / 3), int(self.height() - 100))

        self.person_pic.setScene(self.scene)

        vlayout_person = QVBoxLayout()
        vlayout_person.addWidget(self.person_pic)

        self.btn = QPushButton()
        self.btn.setText("选择图片")
        self.btn.clicked.connect(self.openImage)
        self.btn1 = QPushButton("处理图片")
        self.btn1.clicked.connect(self.processImage)
        self.btn_save = QPushButton("保存图片")
        self.btn_save.clicked.connect(self.saveImage)
        self.btns = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn)
        btn_layout.addWidget(self.btn1)
        btn_layout.addWidget(self.btn_save)
        self.btns.setLayout(btn_layout)
        vlayout_person.addWidget(self.btns)
        self.person.setLayout(vlayout_person)

        # 口罩图片
        self.masks = QGraphicsView()
        self.scene_mask = myQGraphicsScene()

        global itm, itm_pos, maxWidth, maxWidthIndex, selectedRect

        for root, dirs, files in os.walk(IMAGE_DIR):
            for pic in files:
                mask_image_path = os.path.join(IMAGE_DIR, pic)

                image1 = QImage()
                image1.load(mask_image_path)
                self.pixmap1 = QPixmap.fromImage(
                    image1.scaled(QSize(int(self.masks.width()), int(self.masks.height() * 1 / 4)), Qt.KeepAspectRatio,
                                  Qt.SmoothTransformation))
                itm.append(QGraphicsPixmapItem(self.pixmap1))  # 创建像素图元

        for i in range(len(itm)):
            if itm[i].boundingRect().width() > maxWidth:
                maxWidth = itm[i].boundingRect().width()
                maxWidthIndex = i
        for i in range(len(itm)):
            ht = 0
            for j in range(i):
                ht += itm[j].boundingRect().height()
            itm[i].setPos(itm[i].x() + (maxWidth - itm[i].boundingRect().width()) / 2, ht + 20)
            itm_pos.append(itm[i].pos())
            self.scene_mask.addItem(itm[i])
        pen = QPen()
        pen.setColor(QColor(180, 180, 180))
        pen.setWidth(3)
        selectedRect = self.scene_mask.addRect(itm_pos[maxWidthIndex].x(), itm_pos[selectedIndex].y(), maxWidth,
                                               itm[selectedIndex].boundingRect().height(), pen)
        self.masks.setScene(self.scene_mask)
        self.setStyleSheet('''
        QLabel{background:white;}
        ''')
        hlayout = QHBoxLayout()
        hlayout.addStretch(2)
        hlayout.addWidget(self.person)
        hlayout.addStretch(1)
        hlayout.addWidget(self.masks)
        self.setLayout(hlayout)

    def openImage(self):

        global pic_path, selectedFace
        image_person, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        image = QImage()
        image.load(image_person)
        pic_path = image_person
        pixmap = QPixmap.fromImage(image.scaled(self.person_pic.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        item = QGraphicsPixmapItem(pixmap)  # 创建像素图元
        if selectedFace is not None:
            self.scene.removeItem(selectedFace)
            print("remove")
        selectedFace = item
        self.scene.addItem(item)

    def processImage(self):
        print("处理图片")
        print(pic_path)
        print(mask_path)
        if pic_path != "":
            self.faceImageWithMask = FaceMasker(pic_path, mask_path).mask()
            if self.faceImageWithMask is not None:
                faceImage = ImageQt.toqimage(self.faceImageWithMask)
                pixmap = QPixmap.fromImage(faceImage.scaled(self.person_pic.size(), Qt.KeepAspectRatio))
                item = QGraphicsPixmapItem(pixmap)  # 创建像素图元
                self.scene.addItem(item)
            else:
                QMessageBox.critical(self, '警告', '没有检测到人脸', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.critical(self, '警告', '请先选择图片', QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)

    def saveImage(self):
        global count
        count+=1
        path_splits = os.path.splitext(pic_path)
        new_face_path = path_splits[0] + '-with-mask' +str(count) + path_splits[1]
        self.faceImageWithMask.save(new_face_path)
        print(f'Save to {new_face_path}')
        QMessageBox.information(self, '', '保存成功', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

class FaceMasker:
    KEY_FACIAL_FEATURES = ('nose_bridge', 'chin')

    def __init__(self, face_path, mask_path, show=False, model='hog'):
        self.face_path = face_path
        self.mask_path = mask_path
        self.show = show
        self.model = model
        self._face_img: ImageFile = None
        self._mask_img: ImageFile = None

    def mask(self):

        face_image_np = face_recognition.load_image_file(self.face_path)
        face_locations = face_recognition.face_locations(face_image_np, model=self.model)
        face_landmarks = face_recognition.face_landmarks(face_image_np, face_locations)
        self._face_img = Image.fromarray(face_image_np)
        self._mask_img = Image.open(self.mask_path).convert("RGBA")

        found_face = False
        for face_landmark in face_landmarks:
            # check whether facial features meet requirement
            skip = False
            for facial_feature in self.KEY_FACIAL_FEATURES:
                if facial_feature not in face_landmark:
                    skip = True
                    break
            if skip:
                continue

            # mask face
            found_face = True
            self._mask_face(face_landmark)

        if found_face:
            return self._face_img
        else:
            return None

    def _mask_face(self, face_landmark: dict):
        nose_bridge = face_landmark['nose_bridge']
        nose_point = nose_bridge[len(nose_bridge) * 1 // 4]
        nose_v = np.array(nose_point)

        chin = face_landmark['chin']
        chin_len = len(chin)
        chin_bottom_point = chin[chin_len // 2]
        chin_bottom_v = np.array(chin_bottom_point)
        chin_left_point = chin[chin_len // 8]
        chin_right_point = chin[chin_len * 7 // 8]

        # split mask and resize
        width = self._mask_img.width
        height = self._mask_img.height
        width_ratio = 1.2
        new_height = int(np.linalg.norm(nose_v - chin_bottom_v))

        # left
        mask_left_img = self._mask_img.crop((0, 0, width // 2, height))
        mask_left_width = self.get_distance_from_point_to_line(chin_left_point, nose_point, chin_bottom_point)
        mask_left_width = int(mask_left_width * width_ratio)
        mask_left_img = mask_left_img.resize((mask_left_width, new_height))

        # right
        mask_right_img = self._mask_img.crop((width // 2, 0, width, height))
        mask_right_width = self.get_distance_from_point_to_line(chin_right_point, nose_point, chin_bottom_point)
        mask_right_width = int(mask_right_width * width_ratio)
        mask_right_img = mask_right_img.resize((mask_right_width, new_height))

        # merge mask
        size = (mask_left_img.width + mask_right_img.width, new_height)
        mask_img = Image.new('RGBA', size)
        mask_img.paste(mask_left_img, (0, 0), mask_left_img)
        mask_img.paste(mask_right_img, (mask_left_img.width, 0), mask_right_img)

        # rotate mask
        angle = np.arctan2(chin_bottom_point[1] - nose_point[1], chin_bottom_point[0] - nose_point[0])
        rotated_mask_img = mask_img.rotate(angle, expand=True)

        # calculate mask location
        center_x = (nose_point[0] + chin_bottom_point[0]) // 2
        center_y = (nose_point[1] + chin_bottom_point[1]) // 2

        offset = mask_img.width // 2 - mask_left_img.width
        radian = angle * np.pi / 180
        box_x = center_x + int(offset * np.cos(radian)) - rotated_mask_img.width // 2
        box_y = center_y + int(offset * np.sin(radian)) - rotated_mask_img.height // 2

        # add mask
        self._face_img.paste(mask_img, (box_x, box_y), mask_img)

    def showFacewithMask(self):
        maskWindow.showFaceImage(maskWindow, self._face_img)

    @staticmethod
    def get_distance_from_point_to_line(point, line_point1, line_point2):
        distance = np.abs((line_point2[1] - line_point1[1]) * point[0] +
                          (line_point1[0] - line_point2[0]) * point[1] +
                          (line_point2[0] - line_point1[0]) * line_point1[1] +
                          (line_point1[1] - line_point2[1]) * line_point1[0]) / \
                   np.sqrt((line_point2[1] - line_point1[1]) * (line_point2[1] - line_point1[1]) +
                           (line_point1[0] - line_point2[0]) * (line_point1[0] - line_point2[0]))
        return int(distance)


class myQGraphicsScene(QGraphicsScene):
    def __init__(self):
        super(myQGraphicsScene, self).__init__()

    # 重写鼠标点击事件
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        xx = event.scenePos().x()
        yy = event.scenePos().y()
        ht = 0
        global selectedRect, selectedIndex, mask_path, IMAGE_DIR
        for i in range(len(itm)):
            if (yy <= itm[i].boundingRect().height() + ht) & (yy >= ht):
                pen = QPen()
                pen.setColor(QColor(180, 180, 180))
                pen.setWidth(3)
                rect1 = self.addRect(itm_pos[maxWidthIndex].x(), itm_pos[i].y(), maxWidth,
                                     itm[i].boundingRect().height(), pen)
                selectedIndex = i
                self.removeItem(selectedRect)
                selectedRect = rect1
                break
            ht += itm[i].boundingRect().height()
        for root, dirs, files in os.walk(IMAGE_DIR):
            mask_path = os.path.join(IMAGE_DIR, files[selectedIndex])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = maskWindow()
    main.show()
    sys.exit(app.exec_())
    # cli()
