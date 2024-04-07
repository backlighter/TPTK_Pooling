from common.spatial_func import distance
from common.trajectory import Trajectory


class NoiseFilter:
    def filter(self, traj):
        pass

    def get_tid(self, oid, clean_pt_list):
        return oid + '_' + clean_pt_list[0].time.strftime('%Y%m%d%H%M') + '_' + \
               clean_pt_list[-1].time.strftime('%Y%m%d%H%M')


# class HeuristicFilter(NoiseFilter):
#     def __init__(self, max_speed):
#         super(NoiseFilter, self).__init__()
#         self.max_speed = max_speed

#     def filter(self, traj):
#         pt_list = traj.pt_list
#         if len(pt_list) <= 1:
#             return None
#         pre_pt = pt_list[0]
#         clean_pt_list = [pre_pt]
#         for cur_pt in pt_list[1:]:
#             time_span = (cur_pt.time - pre_pt.time).total_seconds()
#             dist = distance(pre_pt, cur_pt)
#             if time_span > 0 and dist / time_span <= self.max_speed:
#                 clean_pt_list.append(cur_pt)
#                 pre_pt = cur_pt
#         if len(clean_pt_list) > 1:
#             return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
#         else:
#             return None

class HeuristicFilter(NoiseFilter):
    def __init__(self, max_speed):
        super(HeuristicFilter, self).__init__()  # 使用正确的基类名称
        self.max_speed = max_speed
        self.csv_file_path = '/data/MaoXiaowei/KDD2024/data/guolv/cleaned_data2.csv'  # 新的 CSV 文件路径

    def filter(self, traj):
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return None
        pre_pt = pt_list[0]
        clean_pt_list = [pre_pt]
        filtered_pt_list = []  # 存储被过滤掉的点
        for cur_pt in pt_list[1:]:
            time_span = (cur_pt.time - pre_pt.time).total_seconds()
            dist = distance(pre_pt, cur_pt)
            if time_span > 0 and dist / time_span <= self.max_speed:
                clean_pt_list.append(cur_pt)
                pre_pt = cur_pt
            else:
                filtered_pt_list.append(cur_pt)  # 将不满足条件的点添加到 filtered_pt_list 中

        if len(clean_pt_list) > 1:
            # 创建 Trajectory 对象，包含清理后的点列表
            cleaned_traj = Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
            # 将被过滤掉的点写入新的 CSV 文件
            self.write_to_csv(filtered_pt_list, self.csv_file_path)
            return cleaned_traj
        else:
            return None

    def write_to_csv(self, data, file_path):
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for item in data:
                row_data = list(item.__dict__.values())
                csv_writer.writerow(row_data)




import csv
class STFilter(NoiseFilter):
    def __init__(self, mbr, start_time, end_time):
        super(STFilter, self).__init__()
        self.mbr = mbr
        self.start_time = start_time
        self.end_time = end_time

    def filter(self, traj):
        cleaned_pt_list=[]
        pt_list = traj.pt_list
        if len(pt_list) <= 1:##如果列表只有一个 则过滤
            cleaned_pt_list.append(pt_list)
            print(pt_list)
            return None
        clean_pt_list = []
        for pt in pt_list:
            if self.start_time <= pt.time < self.end_time and self.mbr.contains(pt.lat, pt.lng):
                clean_pt_list.append(pt)
            else:
                cleaned_pt_list.append(pt)
        

        csv_file_path = '/data/MaoXiaowei/KDD2024/data/guolv/cleaned_data.csv'
        self.write_to_csv(cleaned_pt_list, csv_file_path)
        if len(clean_pt_list) > 1:

            # Writing cleaned_pt_list to CSV
            

            return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
        else:
            return None


    # def write_to_csv(self, data, file_path):
    #         with open(file_path, 'a', newline='') as csvfile:
    #             csv_writer = csv.writer(csvfile)
    #             # Assuming data is a list of lists, each inner list representing a row
    #             csv_writer.writerows(data)

    def write_to_csv(self, data, file_path):
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for item in data:
                row_data = list(item.__dict__.values())
                csv_writer.writerow(row_data)

