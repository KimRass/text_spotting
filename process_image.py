import cv2
from PIL import Image
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def load_image_as_array(img_path="", gray=False):
    img_path = str(img_path)

    if not gray:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    return img


def save_image(img, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if img.ndim == 3:
        cv2.imwrite(filename=str(path), img=img[:, :, :: -1], params=[cv2.IMWRITE_JPEG_QUALITY, 100])
    elif img.ndim == 2:
        cv2.imwrite(filename=str(path), img=img, params=[cv2.IMWRITE_JPEG_QUALITY, 100])


def show_image(img1, img2=None, alpha=0.5):
    plt.figure(figsize=(11, 9))
    plt.imshow(img1)
    if img2 is not None:
        plt.imshow(img2, alpha=alpha)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def draw_rectangles_on_image(img, rectangles1, rectangles2=None, thickness=2):
    img_copied = img.copy()

    for xmin, ymin, xmax, ymax in rectangles1[["xmin", "ymin", "xmax", "ymax"]].values:
        cv2.rectangle(
            img=img_copied, pt1=(xmin, ymin), pt2=(xmax, ymax), color=(255, 0, 0), thickness=thickness
        )
    if rectangles2 is not None:
        for xmin, ymin, xmax, ymax in rectangles2[["xmin", "ymin", "xmax", "ymax"]].values:
            cv2.rectangle(
                img=img_copied, pt1=(xmin, ymin), pt2=(xmax, ymax), color=(0, 0, 255), thickness=thickness
            )

    # if "block" in rectangles.columns.tolist():
    #     for block, xmin, ymin, xmax, ymax in rectangles.drop_duplicates(["block"])[
    #         ["block", "xmin", "ymin", "xmax", "ymax"]
    #     ].values:
    #         cv2.putText(
    #             img=img_copied,
    #             text=str(block),
    #             org=(xmin, ymin),
    #             fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    #             fontScale=0.5,
    #             color=(255, 0, 0),
    #             thickness=2
    #         )
    return img_copied


def set_colormap_jet(img):
    img_jet = cv2.applyColorMap(src=(255 - img), colormap=cv2.COLORMAP_JET)
    return img_jet


def convert_to_pil(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return img


def convert_to_array(img):
    img = np.array(img)
    return img


def blend_two_images(img1, img2, alpha=0.5):
    img1_pil = convert_to_pil(img1)
    img2_pil = convert_to_pil(img2)
    img_blended = convert_to_array(
        Image.blend(im1=img1_pil, im2=img2_pil, alpha=alpha)
    )
    return img_blended


def get_canvas_same_size_as_image(img, black=False):
    if black:
        return np.zeros_like(img).astype("uint8")
    else:
        return (np.ones_like(img) * 255).astype("uint8")


def repaint_segmentation_map(segmap):
    canvas_r = get_canvas_same_size_as_image(segmap, black=True)
    canvas_g = get_canvas_same_size_as_image(segmap, black=True)
    canvas_b = get_canvas_same_size_as_image(segmap, black=True)

    remainders = segmap % 6
    remainders[segmap == 0] = 6

    canvas_r[np.isin(remainders, [1, 2, 4])] = 0
    canvas_r[np.isin(remainders, [3, 5])] = 125
    canvas_r[np.isin(remainders, [0])] = 255
    
    canvas_g[np.isin(remainders, [0, 2, 5])] = 0
    canvas_g[np.isin(remainders, [3, 4])] = 125
    canvas_g[np.isin(remainders, [1])] = 255
    
    canvas_b[np.isin(remainders, [0, 1, 3])] = 0
    canvas_b[np.isin(remainders, [4, 5])] = 125
    canvas_b[np.isin(remainders, [2])] = 255

    dstacked = np.dstack([canvas_r, canvas_g, canvas_b])
    return dstacked


def invert_image(mask):
    return cv2.bitwise_not(mask)


def get_masked_image(img, mask, invert=False):
    if mask.ndim == 3:
        mask = mask[:, :, 0]

    if invert:
        mask = invert_image(mask)
    return cv2.bitwise_and(src1=img, src2=img, mask=mask.astype("uint8"))


def get_pixel_count(arr, sort=False, include_zero=False):
    unique, cnts = np.unique(arr, return_counts=True)
    idx2cnt = dict(zip(unique, cnts))

    if not include_zero:
        if 0 in idx2cnt:
            idx2cnt.pop(0)

    if not sort:
        return idx2cnt
    else:
        return dict(
            sorted(idx2cnt.items(), key=lambda x: x[1], reverse=True)
        )


def get_image_cropped_by_rectangle(img, xmin, ymin, xmax, ymax):
    if img.ndim == 3:
        return img[ymin: ymax, xmin: xmax, :]
    else:
        return img[ymin: ymax, xmin: xmax]


def thin_out_image(img, kernel_shape=(1, 1), iterations=1):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(kernel_shape[1], kernel_shape[0]))
    img = cv2.erode(src=img, kernel=kernel, iterations=iterations)
    return img


def thicken_image(img, kernel_shape=(1, 1), iterations=1):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(kernel_shape[1], kernel_shape[0]))
    img = cv2.dilate(src=img, kernel=kernel, iterations=iterations)
    return img


# img = load_image_as_array("/Users/jongbeom.kim/Documents/공공행정문서 OCR/Training/2.원천데이터_부분라벨링/인.허가/5350108/1993/0001/5350108-1993-0001-0827.jpg")
# img_blur = cv2.GaussianBlur(img, (3,3), 0)
# _, thr = cv2.threshold(src=img_blur, thresh=160, maxval=255, type=cv2.THRESH_BINARY)
# show_image(thr)

# _, thr = cv2.threshold(src=img, thresh=160, maxval=255, type=cv2.THRESH_BINARY)
# show_image(thr)

# thk = thicken_image(
#     thin_out_image(thr)
# )
# thk = thicken_image(
#     thin_out_image(thk)
# )
# thk = thicken_image(
#     thin_out_image(thk)
# )
# thk = thin_out_image(thk, iterations=2)
# # thk = thin_out_image(
# #     thicken_image(thk), iterations=2
# # )
# edge = cv2.Canny(image=thk, threshold1=200, threshold2=255)
# show_image(invert_image(thr[:, :, 0]) + edge)

# show_image(thk)
# # inv = invert_image(thr)

# show_image(thr)


# # dst = cv2.fastNlMeansDenoising(src=img, dts=None, h=10, templateWindowSize=7, searchWIndowSize=21)
# dst = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
# show_image(dst)