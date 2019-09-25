"""The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameInstruction, GameStatus, PlatformAction
)

def ml_loop():
    """The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_position_history=[]
    vx = 0
    vy = 0
    ball_destination = 0
    ball_going_down = 0
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        ball_position_history.append(scene_info.ball)
        platform_center_x = scene_info.platform[0] +20 #platform length = 40
        #print(scene_info.ball)                                                                #球目前的位置印出
        if(len(ball_position_history)) == 1:
            ball_going_down = 0
        elif ball_position_history[-1][1] - ball_position_history[-2][1] > 0 :                #判斷球的方向
            ball_going_down = 1
            vy = ball_position_history[-1][1] - ball_position_history[-2][1]
            vx = ball_position_history[-1][0] - ball_position_history[-2][0]
        else:
            ball_going_down = 0
        print(vx,vy)
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            #scene_info = comm.get_scene_info()
            ball_going_down = 0
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        platform_position_value = ball_position_history[-1][0] - platform_center_x    #判斷球在底盤左邊還是右邊
        if ball_going_down == 0:                                                        #當球往上，底盤回歸中點
            if platform_center_x > 100:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif platform_center_x <100:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            #else:
            #    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        elif ball_going_down == 1:
            if scene_info.ball[1] > 200:
                if (platform_position_value+20) > 0 and vx > 0:                          #底盤最右邊當出發點
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)   #往右移
                elif (platform_position_value-20) < 0 and vx < 0:                        #底盤最左邊當出發點
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)    #往左移