'''
@Descripttion: This is Aoru Xue's demo,which is only for reference
@version: 
@Author: Aoru Xue
@Date: 2019-09-10 13:56:50
@LastEditors: Aoru Xue
@LastEditTime: 2019-10-02 20:14:08
'''
import torch
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim
from model import BasketNet
from torchvision import transforms
from dataset import BasketDataset
from lossfn import BasketLoss
from tqdm import tqdm
from augmentor import BasketAug
from config import *

if __name__ == '__main__':
    transform = BasketAug()
    #transform = transforms.Compose([
    #    transforms.Resize(512),
    #    transforms.ToTensor(),
    #    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    #])
    dataset = BasketDataset("../BasketNet_circle/datasets",transform = transform)
    dataloader = DataLoader(dataset,batch_size = 16,shuffle =  True,num_workers = 6,pin_memory=True)
    
    net = BasketNet(num_classes = num_classes)
    net.cuda()
    #net.load_state_dict(torch.load("./ckpt/3090.pth"))
    optimizer = optim.Adam(net.parameters(),lr = 1e-3)    
    #optimizer = optim.SGD(net.parameters(), lr=1e-1,momentum=0.9,weight_decay=0.)
    #scheduler = optim.lr_scheduler.StepLR(optimizer,100,0.1)
    loss_fn = BasketLoss()
    num_batches = len(dataloader)
    min_loss = float("inf")
    for epoch in range(num_epochs):
        epoch_loss_cls = 0.
        epoch_loss_reg = 0.

        for img,gt_pos,gt_labels,not_ignored in tqdm(dataloader):
            img = img.cuda()
            gt_pos =gt_pos.cuda()
            not_ignored = not_ignored.cuda()
            gt_labels =gt_labels.cuda()
            cls,loc = net(img)
            reg_loss,cls_loss = loss_fn(cls,loc,gt_labels,gt_pos,not_ignored)
            epoch_loss_cls += cls_loss.item()
            epoch_loss_reg += reg_loss.item()
            loss = (reg_loss +  cls_loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        #scheduler.step()
        print("cls_loss:{}---reg_loss:{}".format(epoch_loss_cls/num_batches,epoch_loss_reg/num_batches))
        if (epoch_loss_cls/num_batches + epoch_loss_reg/num_batches) < min_loss:
            min_loss = epoch_loss_cls/num_batches + epoch_loss_reg/num_batches
            torch.save(net.state_dict(),"./ckpt/{}.pth".format(int(epoch_loss_cls/num_batches * 1000 + epoch_loss_reg/num_batches * 1000)))
