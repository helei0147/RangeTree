# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 17:57:54 2020

@author: helei
"""
import random
import numpy as np
import matplotlib.pyplot as plt
import time

def generate_points(point_count, filename=None):
    # generate points in [-1,1] randomly
    points = []
    for i in range(point_count):
        x = random.uniform(-1,1)
        y = random.uniform(-1,1)
        points.append([x,y])
    points = np.array(points)
    if filename==None:
        np.save('1.npy', points)
    else:
        np.save(filename, points)
    return points

def load_points(filename='1.npy'):
    return np.load(filename)
        
class leaf:
    def __init__(self, pos):
        self.pos = pos
        self.yroot=self
        
class node:
    def __init__(self, value, ex_range):
        self.value = value
        self.ex_range = ex_range
        self.yroot = None
        self.left=None
        self.right=None
        
def BuildXTree(points, axis):
    point_count = points.shape[0]
    if(point_count==1):
        return leaf(points[0,:])
    else:
        if(point_count%2==0):
            med_index1 = point_count//2
            med_index0 = med_index1-1
            val = (points[med_index0,0]+points[med_index1,0])/2
            intermediate_node = node(val, [points[0,0], points[-1,0]])
#            print('val {:.3f}, xrange {:.3f} {:.3f}'.format(val, points[0,0], points[-1,0]))
            intermediate_node.left = BuildXTree(points[:med_index1, :], axis)
            intermediate_node.right = BuildXTree(points[med_index1:, :], axis)
            intermediate_node.yroot = MergeYTree(intermediate_node.left.yroot, \
                                                 intermediate_node.right.yroot)
        else:
            med_index = point_count//2
            val = points[med_index,0]
            intermediate_node = node(val, [points[0,0], points[-1,0]])
#            print('val {:.3f}, xrange {:.3f} {:.3f}'.format(val, points[0,0], points[-1,0]))
            intermediate_node.left = BuildXTree(points[:med_index+1, :], axis)
            intermediate_node.right = BuildXTree(points[med_index+1:, :], axis)
            intermediate_node.yroot = MergeYTree(intermediate_node.left.yroot, \
                                                 intermediate_node.right.yroot)
        return intermediate_node
    
def expand_tree(root, buffer): # O(n), n is the leaf count of this tree
    if type(root)==leaf:
        buffer.append(root)
    else:
        expand_tree(root.left, buffer)
        expand_tree(root.right, buffer)

def merge(list1, list2, axis):
    # merge two lists of leaves by the order of axis
    buffer = []
    idx1 = 0
    idx2 = 0
    len1 = len(list1)
    len2 = len(list2)
    while idx1<len1 and idx2<len2:
        if list1[idx1].pos[axis]<list2[idx2].pos[axis]:
            buffer.append(list1[idx1])
            idx1 += 1
        else:
            buffer.append(list2[idx2])
            idx2 += 1
    if idx1==len1:
        for i in range(idx2, len2):
            buffer.append(list2[i])
    elif idx2==len2:
        for i in range(idx1, len1):
            buffer.append(list1[i])
    assert len(buffer)==len1+len2, 'MERGE incomplete'
    return buffer

def generate_ytree(buffer, axis=1):
    leaf_count = len(buffer)
    if leaf_count==1:
        return buffer[0]
    if leaf_count%2==0:
        med_index1 = leaf_count//2
        med_index0 = med_index1 - 1
        val = (buffer[med_index1].pos[axis]+buffer[med_index0].pos[axis])/2
        new_node = node(val, [buffer[0].pos[axis], buffer[-1].pos[axis]])
        new_node.left = generate_ytree(buffer[:med_index1])
        new_node.right = generate_ytree(buffer[med_index1:])
    else:
        med_index = leaf_count//2
        val = buffer[med_index].pos[1]
        new_node = node(val, [buffer[0].pos[axis], buffer[-1].pos[axis]])
        new_node.left = generate_ytree(buffer[:med_index+1])
        new_node.right = generate_ytree(buffer[med_index+1:])
    return new_node
        
def MergeYTree(ytree1, ytree2):
    list1 = []
    list2 = []
    expand_tree(ytree1, list1)
    expand_tree(ytree2, list2)
    total = merge(list1, list2, axis=1)
    ytree = generate_ytree(total)
    return ytree
   
def QueryY(root, yrange, buffer):
    y_min = yrange[0]
    y_max = yrange[1]
    if type(root)==leaf:
        if root.pos[1]<y_max and root.pos[1]>=y_min:
            buffer.append(root.pos)
        return
    assert y_min<=y_max, 'y_min is greater than y_max, ERROR!'
    if root.value<y_min:
        QueryY(root.right, yrange, buffer)
    elif root.value>y_max:
        QueryY(root.left, yrange, buffer)
    elif root.value>=y_min and root.value<y_max:
        QueryY(root.left, yrange, buffer)
        QueryY(root.right, yrange, buffer)
    
    
def query(root, xrange, yrange, buffer): # TODO: add yrange
    x_min, x_max = xrange
    y_min = yrange[0]
    y_max = yrange[1]
    if type(root)==leaf:
        if root.pos[0]<x_max and root.pos[0]>=x_min \
            and root.pos[1]<y_max and root.pos[1]>=y_min:
            buffer.append(root.pos)
        return
    r_min = root.ex_range[0]
    r_max = root.ex_range[1]
#    print('r_min {:.3f} r_max {:.3f}'.format(r_min, r_max))
#    print('x_min {:.3f} x_max {:.3f}\n'.format(x_min, x_max))
    if r_min>=x_min and r_max<x_max:
#        print('r_min {:.3f} r_max {:.3f}'.format(r_min, r_max))
#        print('x_min {:.3f} x_max {:.3f}\n'.format(x_min, x_max))
        QueryY(root.yroot, yrange, buffer)
    else:
        r_min_intersect = r_min>=x_min and r_min<x_max
        r_max_intersect = r_max>=x_min and r_max<x_max
        r_intersect = r_min_intersect or r_max_intersect
        
        x_min_intersect = x_min>=r_min and x_min<r_max
        x_max_intersect = x_max>=r_min and x_max<r_max
        x_intersect = x_min_intersect or x_max_intersect
        if x_intersect or r_intersect:
            query(root.left, xrange, yrange, buffer)
            query(root.right, xrange, yrange, buffer)

def display_tree(node):
    if type(node)==leaf:
        print(node.pos)
    else:
        display_tree(node.left)
        display_tree(node.right)
    
if __name__ == '__main__':
    xrange = [-0.34,0.7]
    yrange = [0.34,0.9]
    iter_count = 10000
    points = load_points('70k.npy')
    ori_points = points
    
    points = points[points[:,0].argsort()]
    print('Start building range tree...')
    time_start = time.time()
    root = BuildXTree(points, 0)
    time_end = time.time()
    time_build_range_tree = time_end-time_start
    print('Range tree built, used {}s'.format(time_build_range_tree))
    
    time_iter = 0
    time_range_tree = time_build_range_tree
    time_container = [[time_build_range_tree, 0]]
    for iter_idx in range(iter_count):
        print('-----------------------------------------------')
        # generate xrange and yrange
        a = random.uniform(-1,1)
        b = random.uniform(-1,1)
        if b>a:
            xrange = [a, b]
        else:
            xrange = [b, a]
        c = random.uniform(-1,1)
        d = random.uniform(-1,1)
        if d>c:
            yrange = [c, d]
        else:
            yrange = [d, c]
        
        print('xrange: {}, yrange: {}'.format(xrange, yrange))
        # use iteration 
        buffer = []
        
#        print('Start query points in range using range tree')
        time_start = time.time()
        query(root, xrange, yrange, buffer)
        time_end = time.time()
        t1 = time_end-time_start
#        print('Query end, used {}s'.format(t1))
        time_range_tree += t1
#        print('Queried points count:', len(buffer))
        
#        print('Start query points in range using a iteration')
        time_start = time.time()
        c = []
        for i in range(points.shape[0]):
            x = points[i,0]
            y = points[i,1]
            x_in_range = x<xrange[1] and x>=xrange[0]
            y_in_range = y<yrange[1] and y>=yrange[0]
            if x_in_range and y_in_range:
                c.append([x,y])
        time_end = time.time()
        t2 = time_end-time_start
#        print('Query end. time usage: {}s'.format(t2))
        time_iter += t2
#        print('Queried points count:', len(c))
        
        time_container.append([t1, t2])
        if len(buffer)==len(c):
            print('CORRECT')   
        buffer = np.array(buffer)
        # # plot results in range [-1, 1]
        # plt.figure()
        # plt.axis('equal')
        # plt.xlim((-1,1))
        # plt.ylim((-1,1))
        # plt.plot(points[:,0], points[:,1], 'r.')
        # plt.plot(buffer[:,0], buffer[:,1], 'b.')
    print('range query count: {}'.format(iter_count))
    print('query time consumption of iteration: {}s'.format(time_iter))
    print('query time consumption of range tree: {}s'.format(time_range_tree))
    np.save('time{}.npy'.format(iter_count), time_container)