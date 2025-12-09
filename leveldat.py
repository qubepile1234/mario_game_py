def set_level_data():
        map level1={
        list['ground']=[0,GROUND_HEIGHT,MAP_WIDTH,(0,222,0)]
        list['wall']=[0, 0, HEIGHT,(255,0,0)][MAP_WIDTH-1, 0, HEIGHT,(0,255,255)]
        list['pipe']=[40, GROUND_HEIGHT, 40, 80, (221,112,112)][200, GROUND_HEIGHT, 83, 120, (22,22,131)]

        }
        set_level(level1)
        #可能有level2但暂时搁置
        

def set_level(map level{}):
    for item in level['ground']:
        set_ground(item)
    for item in level['wall']:
        set_wall(item)
    for item in level['pipe']:
        set_pipe(item)
def set_ground(list ground):
    ground_line = LineCollider(x=ground[0],y=ground[1],length=ground[2], 'horizontal', color=ground[3])
    self.horizontal_lines.add(ground_line)
def set_wall(list wall):
    wall_line= LineCollider(x=wall[0],y=wall[1],length=wall[2], 'vertical', color=wall[3])
    self.vertical_lines.add(wall_line)
def set_pipe(list pipe):
    self.pipe1 = self.create_pipe(x=pipe[0],y=pipe[1],width=wall[2], height=pipe[3] ,color=pipe[4])
