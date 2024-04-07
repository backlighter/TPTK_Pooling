# a tutorial example based on T-Drive dataset
import os
import sys

from common.road_network import load_rn_shp
from common.trajectory import Trajectory, store_traj_file, parse_traj_file,store_traj_file_mm_tdrive
from common.trajectory import STPoint
from noise_filtering import STFilter, HeuristicFilter
from segmentation import TimeIntervalSegmentation, StayPointSegmentation
from map_matching.hmm.hmm_map_matcher import TIHMMMapMatcher
from common.mbr import MBR
from datetime import datetime
import os
from tqdm import tqdm
import argparse
from statistics import statistics



'''
def parse_tdrive(filename, tdrive_root_dir):
    oid = filename.replace('.txt', '')
    with open(os.path.join(tdrive_root_dir, filename), 'r') as f:
        pt_list = []
        for line in f.readlines():
            attrs = line.strip('\n').split(',')
            lat = float(attrs[3])
            lng = float(attrs[2])
            time = datetime.strptime(attrs[1], '%Y-%m-%d %H:%M:%S')
            pt_list.append(STPoint(lat, lng, time))
    if len(pt_list) > 1:
        return Trajectory(oid, 0, pt_list)
    else:
        return None
'''

#修改
def parse_tdrive(filename, tdrive_root_dir):
    oid = filename.replace('.txt', '')
    with open(os.path.join(tdrive_root_dir, filename), 'r') as f:
        pt_list = []
        for i, line in enumerate(f.readlines()):
            # Skip the first line
            if i == 0:
                continue

            attrs = line.strip('\n').split(',')
            lat = float(attrs[3])
            lng = float(attrs[2])
            time = datetime.strptime(attrs[1], '%Y/%m/%d %H:%M:%S')
            pt_list.append(STPoint(lat, lng, time))

    if len(pt_list) > 1:
        return Trajectory(oid, 0, pt_list)
    else:
        return None

def do_clean(raw_traj, filters, segmentations):
    clean_traj = raw_traj
    for filter in filters:
        clean_traj = filter.filter(clean_traj)
        if clean_traj is None:
            return []
    clean_traj_list = [clean_traj]
    for seg in segmentations:
        tmp_clean_traj_list = []
        for clean_traj in clean_traj_list:
            segment_trajs = seg.segment(clean_traj)
            tmp_clean_traj_list.extend(segment_trajs)
        clean_traj_list = tmp_clean_traj_list
    return clean_traj_list


# def do_clean(raw_traj, filters, segmentations):
#     # 新增一个列表，用于保存被过滤掉的轨迹
#     filtered_out_traj_list = []

#     clean_traj = raw_traj
#     for filter in filters:
#         clean_traj = filter.filter(clean_traj)
#         if clean_traj is None:
#             print("raw_traj",raw_traj)
#             #将被过滤掉的轨迹保存到列表中
#             filtered_out_traj_list.append(raw_traj)
#             return []
#     clean_traj_list = [clean_traj]
#     for seg in segmentations:
#         tmp_clean_traj_list = []
#         for clean_traj in clean_traj_list:
#             segment_trajs = seg.segment(clean_traj)
#             tmp_clean_traj_list.extend(segment_trajs)
#         clean_traj_list = tmp_clean_traj_list
    
    # # 如果 clean_traj_list 为空，说明所有轨迹都被过滤掉了，将原始轨迹保存到列表中
    # if not clean_traj_list:
    #     filtered_out_traj_list.append(raw_traj)
    
    
    # return clean_traj_list,filtered_out_traj_list

def clean_tdrive(tdrive_root_dir, clean_traj_dir):
    start_time = datetime(2018, 11, 1)
    end_time = datetime(2018, 11, 17)
    mbr = MBR(30.65, 104.02, 30.78, 104.15)
    st_filter = STFilter(mbr, start_time, end_time)
    heuristic_filter = HeuristicFilter(max_speed=35)
    filters = [st_filter, heuristic_filter]
    ti_seg = TimeIntervalSegmentation(max_time_interval_min=2)
    sp_seg = StayPointSegmentation(dist_thresh_meter=100, max_stay_time_min=15)
    segs = [ti_seg, sp_seg]
    for filename in tqdm(os.listdir(tdrive_root_dir)):
        raw_traj = parse_tdrive(filename, tdrive_root_dir)
        if raw_traj is None:
            continue
        clean_trajs = do_clean(raw_traj, filters, segs)
        if len(clean_trajs) > 0:
            store_traj_file(clean_trajs, os.path.join(clean_traj_dir, filename))


def clean_tdrive_TO_Map(tdrive_root_dir, clean_traj_dir):
    clean_trajs_List=[]
    start_time = datetime(2018, 11, 1)
    end_time = datetime(2018, 11, 17)
    mbr = MBR(30.65, 104.06, 30.72, 104.11)
    #mbr = MBR(34.224839, 108.938916, 34.261751, 108.982253)
    st_filter = STFilter(mbr, start_time, end_time)
    heuristic_filter = HeuristicFilter(max_speed=35)
    filters = [st_filter, heuristic_filter]
    ti_seg = TimeIntervalSegmentation(max_time_interval_min=6)
    sp_seg = StayPointSegmentation(dist_thresh_meter=100, max_stay_time_min=15)
    segs = [ti_seg, sp_seg]
    for filename in tqdm(os.listdir(tdrive_root_dir)):
        raw_traj = parse_tdrive(filename, tdrive_root_dir)
        if raw_traj is None:
            continue
        clean_trajs = do_clean(raw_traj, filters, segs)
        if len(clean_trajs) > 0:
            # print(clean_trajs)
            clean_trajs_List.extend(clean_trajs)
            # store_traj_file(clean_trajs, os.path.join(clean_traj_dir, filename))
        #传入clean_trajs_dicts
    store_traj_file_mm_tdrive(clean_trajs_List, os.path.join(clean_traj_dir, "ALL_Traj.csv"),
                    os.path.join(clean_traj_dir, "TrajID_Map.csv"),traj_type='raw')

# def clean_tdrive(tdrive_root_dir, clean_traj_dir):

    
#     os.makedirs(filtered_out_traj_dir, exist_ok=True)

#     start_time = datetime(2018, 11, 1)
#     end_time = datetime(2018, 11, 3)
#     mbr = MBR(30.6, 104.02, 30.78, 104.15)
#     st_filter = STFilter(mbr, start_time, end_time)
#     heuristic_filter = HeuristicFilter(max_speed=35)
#     filters = [st_filter, heuristic_filter]
#     ti_seg = TimeIntervalSegmentation(max_time_interval_min=6)
#     sp_seg = StayPointSegmentation(dist_thresh_meter=100, max_stay_time_min=15)
#     segs = [ti_seg, sp_seg]
#     for filename in tqdm(os.listdir(tdrive_root_dir)):
#         raw_traj = parse_tdrive(filename, tdrive_root_dir)
#         if raw_traj is None:
#             continue
#         clean_trajs= do_clean(raw_traj, filters, segs)
#         if len(clean_trajs) > 0:
#             store_traj_file(clean_trajs, os.path.join(clean_traj_dir, filename))


        
        
'''
def mm_tdrive(clean_traj_dir, mm_traj_dir, rn_path):
    rn = load_rn_shp(rn_path, is_directed=True)
    map_matcher = TIHMMMapMatcher(rn)
    all_trajs = []
    for filename in tqdm(os.listdir(clean_traj_dir)):
        clean_trajs = parse_traj_file(os.path.join(clean_traj_dir, filename))
        mm_trajs = [map_matcher.match(clean_traj) for clean_traj in clean_trajs]
        #store_traj_file(mm_trajs, os.path.join(mm_traj_dir, filename), traj_type='mm')
        all_trajs.extend(mm_trajs)
    
    # 将所有处理过的轨迹数据保存到同一个文件
    #os.path.join(mm_traj_dir, "ALL_Traj.csv") 存放所有的轨迹数据,
    #os.path.join(mm_traj_dir, "TrajID_Map.csv") 存放轨迹数据和统计信息的字典

    #单进程
    store_traj_file_mm_tdrive(all_trajs, os.path.join(mm_traj_dir, "ALL_Traj.csv"),
            os.path.join(mm_traj_dir, "TrajID_Map.csv"), traj_type='mm')

    #多进程
    # store_traj_file_mm_tdrive_parallel(all_trajs, os.path.join(mm_traj_dir, "ALL_Traj.csv"),
    #         os.path.join(mm_traj_dir, "TrajID_Map.csv"), traj_type='mm')
    
'''
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import Manager


def process_file(filename, clean_traj_dir,result_list):
    map_matcher=TIHMMMapMatcher(rn)
    # print(map_matcher)
    clean_trajs = parse_traj_file(os.path.join(clean_traj_dir, filename))
    mm_trajs = [map_matcher.match(clean_traj) for clean_traj in clean_trajs]
    # print("mm_trajs为",mm_trajs)
    result_list.extend(mm_trajs)
    
    
manager=Manager()
all_trajs = manager.list()
# 加载 rn
# 定义全局变量 rn
rn = None

def mm_tdrive(clean_traj_dir, mm_traj_dir,rn_path):
    
    global rn  # 使用 global 关键字声明 rn 为全局变量
    global all_trajs  # 使用 global 关键字声明 all_trajs 为全局变量
    rn = load_rn_shp(rn_path, is_directed=True)

    filenames = os.listdir(clean_traj_dir)
    num_processes=32
    
    # 使用ProcessPoolExecutor实现多进程处理
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # with Manager() as manager:
        #     all_trajs = manager.list()
        process_function = partial(process_file, clean_traj_dir=clean_traj_dir, result_list=all_trajs)
        list(tqdm(executor.map(process_function, filenames), total=len(filenames)))
    # print("all_trajs为",list(all_trajs))
    # 将所有处理过的轨迹数据保存到同一个文件
    # os.path.join(mm_traj_dir, "ALL_Traj.csv") 存放所有的轨迹数据,
    # os.path.join(mm_traj_dir, "TrajID_Map.csv") 存放轨迹数据和统计信息的字典

    # 单进程
    store_traj_file_mm_tdrive(all_trajs, os.path.join(mm_traj_dir, "ALL_Traj.csv"),
                            os.path.join(mm_traj_dir, "TrajID_Map.csv"), traj_type='mm')
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tdrive_root_dir', help='the directory of the TDrive dataset')
    parser.add_argument('--clean_traj_dir', help='the directory of the cleaned trajectories')
    parser.add_argument('--rn_path', help='the road network data path generated by osm2rn')
    parser.add_argument('--mm_traj_dir', help='the directory of the map-matched trajectories')
    parser.add_argument('--phase', help='the preprocessing phase [clean,mm,stat]')

    opt = parser.parse_args()
    # print(opt)

    if opt.phase == 'clean':
        #clean_tdrive_TO_Map(opt.tdrive_root_dir, opt.clean_traj_dir)
        # clean_tdrive(opt.tdrive_root_dir, opt.clean_traj_dir)
        # for day in range(1, 17):
        #     day_str = f'201811{day:02d}'
        #     tdrive_dir = os.path.join(opt.tdrive_root_dir, day_str)
        #     print("tdrive_dir为",tdrive_dir)
        #     clean_traj_dir = os.path.join(opt.clean_traj_dir, day_str)
        #     print("clean_traj_dir存储为",clean_traj_dir)

        #     # 检查clean_traj_dir是否存在，如果不存在则创建
        #     if not os.path.exists(clean_traj_dir):
        #         os.makedirs(clean_traj_dir)
        tdrive_dir=opt.tdrive_root_dir
        clean_traj_dir=opt.clean_traj_dir
        clean_tdrive_TO_Map(tdrive_dir, clean_traj_dir)
    elif opt.phase == 'mm':
        mm_tdrive(opt.clean_traj_dir, opt.mm_traj_dir, opt.rn_path)
    elif opt.phase == 'stat':
        statistics(opt.clean_traj_dir)
    else:
        raise Exception('unknown phase')
