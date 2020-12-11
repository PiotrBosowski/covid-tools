import os
import shutil
import torch
import torchvision
from fsplit.filesplit import Filesplit
from PIL import Image


def split_by_modality(args):
    split_dataset_by_modality(args.path, args.ext)


labels = ['frontal-nega', 'frontal-posi', 'side-nega', 'side-posi']

transformer = torchvision.transforms.Compose([
    torchvision.transforms.Resize(size=(224, 224)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def get_model():
    model_folder = os.path.join(os.environ['CovidTools'], 'mod_split_model')
    model_path = os.path.join(model_folder, 'model.pt')
    if not os.path.exists(model_path):
        fs = Filesplit()
        fs.merge(input_dir=os.path.join(model_folder, 'parts'),
                 output_file=os.path.join(model_path),
                 cleanup=False)
    return torch.load(model_path)


# def split_dataset_by_modality(dataset_path, image_extension):
#     for label in labels:
#         os.makedirs(os.path.join(dataset_path, label), exist_ok=False)
#     model = get_model().to('cpu')
#     images = [os.path.join(dataset_path, image) for image in os.listdir(dataset_path) if image.endswith(image_extension)]
#     with torch.no_grad():
#         model.eval()
#         for index, image in enumerate(images):
#             try:
#                 with Image.open(image).convert('RGB') as img:
#                     transformed = transformer(img)
#                     img_unsqueezed = transformed.unsqueeze(0)
#                     prediction = model(img_unsqueezed)
#                     _, prediction = torch.max(prediction, 1)
#                     print([index + 1], labels[prediction.item()])
#                 shutil.copy(image, os.path.join(dataset_path, labels[prediction.item()], os.path.basename(image)))
#             except Exception as ex:
#                 print(f"Error processing image {os.path.basename(image)}, {ex}")

def split_dataset_by_modality(dataset_path, image_extension):
    for label in labels:
        os.makedirs(os.path.join(dataset_path, label), exist_ok=True)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = get_model().to(device)
    images = [os.path.join(dataset_path, image) for image in os.listdir(dataset_path) if image.endswith(image_extension)]
    with torch.no_grad():
        model.eval()
        for index, image in enumerate(images):
            try:
                with Image.open(image).convert('RGB') as img:
                    transformed = transformer(img)
                    img_unsqueezed = transformed.unsqueeze(0)
                    prediction = model(img_unsqueezed.to(device))
                    _, prediction = torch.max(prediction, 1)
                    print([index + 1], labels[prediction.item()])
                shutil.copy(image, os.path.join(dataset_path, labels[prediction.item()], os.path.basename(image)))
            except Exception as ex:
                print(f"Error processing image {os.path.basename(image)}, {ex}")

if __name__ == '__main__':
    split_dataset_by_modality('/home/peter/media/data/covid-19/cr/03_BIMCV-COVID-19-nega/converted/covid-or-healthy', '.png')