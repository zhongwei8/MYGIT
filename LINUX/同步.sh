###
 # @Author       : Tianzw
 # @Date         : 2021-03-16 10:34:10
 # @LastEditors  : Please set LastEditors
 # @LastEditTime : 2021-03-16 10:35:03
 # @FilePath     : /my_github/LINUX/同步.sh
###

remote_path=fds://new-sensor-bucket/libai/heartrate/data-collect/
local_path=/home/mi/data/new-sensor-bucket/libai/heartrate/data-collect/
fdscli sync -f $remote_path $local_path
