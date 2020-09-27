import json
import sys
from datetime import datetime
from random import randint

import pygame as pg

import pyganim
from highscore import load_highscore_data, save_highscore_data
from state_engine import GameState
from text_wrap import draw_text
from util import between


class TitleScreen(GameState):
    def __init__(self):
        super(TitleScreen, self).__init__()
        self.next_state = "PLAYERSELECT"
        self.font_big = pg.font.Font('resources/fonts/aesymatt.ttf', 90)
        self.font = pg.font.Font('resources/fonts/aesymatt.ttf', 50)
        self.font_small = pg.font.Font('resources/fonts/aesymatt.ttf', 20)
        self.persist['highscore'] = load_highscore_data()

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_SPACE) == 'released':
            self.done = True

    def draw(self, surface):
        surface.fill((0, 0, 0))
        rendered_white_text = self.font_big.render('The High Noon Duel', False, (255, 255, 255))
        x = int(int(1024 - rendered_white_text.get_rect().width)/2)
        y = 60
        # for offset in [{'x': -1, 'y': 0}, {'x': 1, 'y': 0}, {'x': 0, 'y': -1}, {'x': 0, 'y': 1}]:
        #     surface.blit(rendered_white_text, (x + offset['x'], y + offset['y']))
        surface.blit(rendered_white_text, (x, y))

        y = 200
        entries = list()
        highscore = self.persist['highscore']
        if highscore['quickest_draw']:
            entries.append(f"- Quickest draw {highscore['quickest_draw']} ms")
        if highscore['hero']['wins'] < highscore['outlaw']['wins']:
            entries.append(f"- {highscore['outlaw']['wins']} wins as Outlaw over {highscore['outlaw']['loses']} loses")
            entries.append(f"- {highscore['hero']['wins']} wins as Hero over {highscore['hero']['loses']} loses")
        else:
            entries.append(f"- {highscore['hero']['wins']} wins as Hero over {highscore['hero']['loses']} loses")
            entries.append(f"- {highscore['outlaw']['wins']} wins as Outlaw over {highscore['outlaw']['loses']} loses")
        if highscore['draws']:
            entries.append(f"- And a total of {highscore['draws']} draws")

        for entry in entries:
            stat_text = self.font.render(entry, False, (255, 255, 255))
            surface.blit(stat_text, (x, y))
            y += 50

        action_text = self.font_small.render('Press space to start', False, (200, 200, 200))
        x = int(int(1024 - action_text.get_rect().width)/2)
        y = 500
        surface.blit(action_text, (x, y))

    def update(self, dt):
        pass


class PlayerSelect(GameState):
    def __init__(self):
        super(PlayerSelect, self).__init__()
        self.font = pg.font.Font('resources/fonts/aesymatt.ttf', 50)
        self.font_small = pg.font.Font('resources/fonts/aesymatt.ttf', 20)
        self.shooters = {
            1: pg.image.load('resources/images/shooter-1.jpg'),
            2: pg.image.load('resources/images/shooter-2.jpg')
        }

        self.clipping = {
            1: {
                'position': {'x': 120, 'y': 100},
                'offset': {'x': 510, 'y': 130},
                'width': 400,
                'height': 400,
                'zoom': 0.7,
                'name': 'Hero'
            },
            2: {
                'position': {'x': 540, 'y': 100},
                'offset': {'x': 510, 'y': 310},
                'width': 400,
                'height': 400,
                'zoom': 0.7,
                'name': 'Outlaw'
            }
        }

        self.target = 1
        self.next_state = "INSTRUCTIONS"

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_LEFT) == 'pressed':
            self.target = 1
        if key_events.get(pg.K_RIGHT) == 'pressed':
            self.target = 2

        if key_events.get(pg.K_SPACE) == 'released':
            self.persist['player_character'] = self.target
            self.done = True

    def draw(self, surface):
        surface.fill((0, 0, 0))

        rendered_text = self.font.render(f"You are the {self.clipping[self.target]['name']} of this story", False, (255, 255, 255))
        surface.blit(rendered_text, (int(int(1024 - rendered_text.get_rect().width) / 2), 20))

        rendered_text = self.font_small.render("Press space to select your character", False, (200, 200, 200))
        surface.blit(rendered_text, (int(940 - rendered_text.get_rect().width), 510))

        for shooter_id, shooter_image in self.shooters.items():
            shooter_rect = shooter_image.get_rect()
            shooter = pg.transform.scale(shooter_image, (int(shooter_rect.width * self.clipping[shooter_id]['zoom']), int(shooter_rect.height * self.clipping[shooter_id]['zoom'])))

            shooter.set_clip(pg.Rect(self.clipping[shooter_id]['offset']['x'], self.clipping[shooter_id]['offset']['y'], self.clipping[shooter_id]['width'], self.clipping[shooter_id]['height']))
            shooter_clip = shooter.get_clip()
            shooter_clipped = shooter.subsurface(shooter_clip)
            surface.blit(shooter_clipped, (self.clipping[shooter_id]['position']['x'], self.clipping[shooter_id]['position']['y'], self.clipping[shooter_id]['width'], self.clipping[shooter_id]['height']))

        pg.draw.rect(surface, (255, 255, 255), (self.clipping[self.target]['position']['x'], self.clipping[self.target]['position']['y'],
                                                self.clipping[self.target]['width'], self.clipping[self.target]['height']),
                     width=3)

    def update(self, dt):
        pass


class Instructions(GameState):
    def __init__(self):
        super(Instructions, self).__init__()
        self.font = pg.font.Font('resources/fonts/aesymatt.ttf', 40)
        self.font_small = pg.font.Font('resources/fonts/aesymatt.ttf', 20)
        with open('resources/texts/instructions.txt') as f:
            self.instruction_text = f.read()
        self.render_text = self.instruction_text
        self.draw_next_page = True
        self.next_state = "COINTOSS"

    def startup(self, persistent):
        self.persist = persistent
        self.render_text = self.instruction_text
        self.draw_next_page = True

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_SPACE) == 'released':
            if self.render_text:
                self.draw_next_page = True
            else:
                self.done = True
        if key_events.get(pg.K_RETURN) == 'released':
            self.done = True

    def draw(self, surface):
        if self.draw_next_page:
            surface.fill((0, 0, 0))
            self.render_text = draw_text(surface, self.render_text, (255, 255, 255), (110, 100, 800, 400), self.font)
            pg.draw.rect(surface, (255, 255, 255), (70, 90, 880, 400), width=3)
            if self.render_text:
                text_box_text = 'spacebar next page or enter to skip'
            else:
                text_box_text = 'spacebar or enter to skip'
            rendered_text = self.font_small.render(text_box_text, False, (200, 200, 200))
            surface.blit(rendered_text, (int(950 - rendered_text.get_rect().width), 500))
            self.draw_next_page = False

    def update(self, dt):
        pass


class CoinTossScreen(GameState):
    def __init__(self):
        super(CoinTossScreen, self).__init__()
        self.shooter_1 = pg.image.load('resources/images/shooter-1.jpg')
        self.shooter_2 = pg.image.load('resources/images/shooter-2.jpg')
        self.background = pg.image.load('resources/images/coin-toss-bg.jpg')
        self.thut = pg.image.load('resources/images/thut.png')

        coin_toss_sheet = pg.image.load('resources/sprite_sheets/coin_toss.png')
        coin_toss = []
        for frame_count in range(0, 8):
            coin_toss_sheet.set_clip(pg.Rect(frame_count * 16, 0, 16, 16))
            coin_toss_clip = coin_toss_sheet.get_clip()
            coin_toss.append((pg.transform.scale(coin_toss_sheet.subsurface(coin_toss_clip), (125, 125)), 0.15))
        self.coin_toss = pyganim.PygAnimation(coin_toss)
        self.coin_velocity = None
        self.coin_toss_active = False
        self.thut_active = False
        self.coin_hit = None

        self.next_state = "SHOOTOUT"

        self.clipping = {
            1: {'x': 680, 'y': 200},
            2: {'x': 690, 'y': 490},
            'background': {'x': 0, 'y': 0}
        }
        self.positioning = {
            'coin': {'x': 800, 'y': 350},
            'shade': {'x': 800, 'y': 930}
        }
        self.timing = {
            'coin': 0
        }

    def startup(self, persistent):
        self.persist = persistent
        self.slider = {'value': 0, 'direction': -1, 'speed': 45, 'spread': 180}
        self.slider['target'] = randint(80 + int(self.slider['spread'] / 2), 940 - int(self.slider['spread'] / 2))
        self.shots_taken = None
        self.position = {
            1: {'x': 230, 'y': 360},
            2: {'x': 640, 'y': 370}
        }
        self.coin_toss.pause()
        self.coin_toss.currentFrameNum = 0
        self.coin_velocity = None
        self.coin_toss_active = False
        self.thut_active = False
        self.coin_hit = None
        self.clipping = {
            1: {'x': 680, 'y': 200},
            2: {'x': 690, 'y': 490},
            'background': {'x': 0, 'y': 0}
        }
        self.positioning = {
            'coin': {'x': 800, 'y': 350},
            'shade': {'x': 800, 'y': 930}
        }
        self.timing = {
            'coin': 0
        }

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_SPACE) == 'pressed' and self.coin_toss_active is False:
            self.coin_toss_active = True
            self.coin_velocity = -80
            self.coin_toss.play()
        if key_events.get(pg.K_SPACE) == 'released':
            if self.thut_active is False:
                self.done = True
                self.persist['reaction'] = None
            if self.thut_active is True:
                self.done = True
                self.persist['reaction'] = (datetime.utcnow() - self.coin_hit).microseconds
            if randint(0, 10) % 5 == 0:
                self.persist['enemy-reaction'] = None
            else:
                self.persist['enemy-reaction'] = randint(80000, 240000)

    def draw(self, surface):
        surface.fill((0, 0, 0))

        self.shooter_1.set_clip(pg.Rect(self.clipping[1]['x'], self.clipping[1]['y'], 700, 276))
        shooter_1_clip = self.shooter_1.get_clip()
        shooter_1_clipped = self.shooter_1.subsurface(shooter_1_clip)
        surface.blit(shooter_1_clipped, (8, 8, 700, 276))

        self.shooter_2.set_clip(pg.Rect(self.clipping[2]['x'], self.clipping[2]['y'], 700, 276))
        shooter_2_clip = self.shooter_2.get_clip()
        shooter_2_clipped = self.shooter_2.subsurface(shooter_2_clip)
        surface.blit(shooter_2_clipped, (8, 292, 700, 276))

        self.background.set_clip(pg.Rect(
            self.clipping['background']['x'], self.clipping['background']['y'], 301, 560))
        background_clip = self.background.get_clip()
        background_clipped = self.background.subsurface(background_clip)
        surface.blit(background_clipped, (716, 8, 301, 560))

        mask = pg.mask.from_surface(self.coin_toss.getCurrentFrame())
        mask_outline = mask.outline()
        n = 0
        for point in mask_outline:
            mask_outline[n] = (point[0] + self.positioning['shade']['x'], point[1] + self.positioning['shade']['y'] - self.clipping['background']['y'])
            n += 1
        pg.draw.polygon(surface, (0, 0, 0), mask_outline, 0)

        surface.blit(self.coin_toss.getCurrentFrame(), (self.positioning['coin']['x'], self.positioning['coin']['y']))

        if self.thut_active:
            surface.blit(pg.transform.scale(self.thut, (228, 114)), (self.positioning['coin']['x'] - 50, self.positioning['coin']['y'] + 10))

    def update(self, dt):
        self.timing['coin'] -= dt
        if self.coin_toss_active and self.timing['coin'] <= 0:
            if self.coin_velocity is not None:
                self.positioning['coin']['y'] += self.coin_velocity
                self.coin_velocity += 10
                if self.coin_velocity > 80:
                    self.coin_velocity = 80
            self.timing['coin'] = 100
        elif self.clipping['background']['y'] >= 500 and self.thut_active is False:
            self.coin_toss.pause()
            self.coin_toss.currentFrameNum = 7
            self.thut_active = True
            self.coin_hit = datetime.utcnow()
        elif self.positioning['coin']['y'] >= 400 and self.thut_active is False:
            self.coin_velocity = None
            self.clipping['background']['y'] += 10


class ShootOut(GameState):
    def __init__(self):
        super(ShootOut, self).__init__()
        self.background = pg.image.load('resources/images/duel.png')
        self.player_1 = pg.image.load('resources/images/player-1.png')
        self.player_1_shoot = pg.image.load('resources/images/player-1-shoot.png')
        self.player_2 = pg.image.load('resources/images/player-2.png')
        self.player_2_shoot = pg.image.load('resources/images/player-2-shoot.png')
        self.slide_marker = pg.image.load('resources/images/slide-marker.png')
        self.range_marker_left = pg.image.load('resources/images/range-marker-left.png')
        self.range_marker_right = pg.image.load('resources/images/range-marker-right.png')
        self.shots_taken = None
        self.position = None
        self.slider = None
        self.next_state = "DUSTSETTLING"

    def startup(self, persistent):
        self.persist = persistent
        self.slider = {'value': 0, 'direction': -1, 'speed': 45, 'spread': 180}
        self.slider['target'] = randint(80 + int(self.slider['spread'] / 2), 940 - int(self.slider['spread'] / 2))
        self.shots_taken = None
        self.position = {
            1: {'x': 230, 'y': 360},
            2: {'x': 640, 'y': 370}
        }

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_q) == 'released':
            pg.quit()
            sys.exit()

        if key_events.get(pg.K_SPACE) == 'pressed':
            if self.shots_taken is None:
                self.shots_taken = datetime.utcnow()
                current_value = self.slider['value']
                lower_target = self.slider['target'] - int(self.slider['spread'] / 2)
                upper_target = self.slider['target'] + int(self.slider['spread'] / 2)
                self.persist['hit'] = {
                    'by_player': between(current_value, lower_target, upper_target),
                    'by_enemy': int(randint(0, 9) % 2) == 0
                }

    def update(self, dt):
        if self.shots_taken is None:
            if self.slider['value'] < 40:
                self.slider['value'] = 40
                self.slider['direction'] = 1
            elif self.slider['value'] > 980:
                self.slider['value'] = 980
                self.slider['direction'] = -1
            self.slider['value'] += int(self.slider['speed'] * self.slider['direction'])

            if self.slider['spread'] > -10:
                self.slider['spread'] -= 1
            elif self.slider['spread'] <= -10:
                self.shots_taken = datetime.utcnow()
                self.persist['hit'] = {
                    'by_player': False,
                    'by_enemy': True
                }
                self.persist['reaction'] = False
                self.done = True
        elif (datetime.utcnow() - self.shots_taken).microseconds > 200000:
            self.done = True

    def draw(self, surface):
        surface.fill((0, 0, 0))
        surface.blit(pg.transform.scale(self.background, (1024, 576)), (0, 0))

        if self.shots_taken:
            surface.blit(pg.transform.scale(self.player_1_shoot, (int(self.player_1_shoot.get_rect().width / 1.875), int(self.player_1_shoot.get_rect().height / 1.875))), (self.position[1]['x'], self.position[1]['y']))
            surface.blit(pg.transform.scale(self.player_2_shoot, (int(self.player_2_shoot.get_rect().width / 1.875), int(self.player_2_shoot.get_rect().height / 1.875))), (self.position[2]['x'], self.position[2]['y']))
        else:
            surface.blit(pg.transform.scale(self.player_1, (int(self.player_1.get_rect().width / 1.875), int(self.player_1.get_rect().height / 1.875))), (self.position[1]['x'], self.position[1]['y']))
            surface.blit(pg.transform.scale(self.player_2, (int(self.player_2.get_rect().width / 1.875), int(self.player_2.get_rect().height / 1.875))), (self.position[2]['x'], self.position[2]['y']))

        pg.draw.line(surface, (255, 255, 255), (40, 500), (980, 500), width=3)
        surface.blit(pg.transform.scale(self.range_marker_left, (14, 28)), (40 + self.slider['target'] - int(self.slider['spread'] / 2) - 14, 488))
        surface.blit(pg.transform.scale(self.range_marker_right, (14, 28)), (40 + self.slider['target'] + int(self.slider['spread'] / 2) + 14, 488))
        surface.blit(pg.transform.scale(self.slide_marker, (14, 28)), (40 + self.slider['value'] - 7, 488))


class DustSettling(GameState):
    def __init__(self):
        super(DustSettling, self).__init__()
        self.font_big = pg.font.Font('resources/fonts/aesymatt.ttf', 60)
        self.font = pg.font.Font('resources/fonts/aesymatt.ttf', 40)
        self.font_small = pg.font.Font('resources/fonts/aesymatt.ttf', 20)
        self.player_result = None
        self.player_comment = None
        self.render_text = None
        self.draw_next_page = True
        self.next_state = 'TITLESCREEN'

    def startup(self, persistent):
        print(persistent)
        self.persist = persistent
        # determine outcome
        if self.persist['reaction'] is False:
            # player dies early draw
            player_result = 'You loose'
            if self.persist['player_character'] == 1:
                self.persist['highscore']['hero']['loses'] += 1
                player_comment = 'As you faced the outlaw his gaze froze you in you place. Unable to move the outlaw took aim and shot you straight trough the heart. You heard the murmering of the crowed in the town.'
            else:
                self.persist['highscore']['outlaw']['loses'] += 1
                player_comment = 'The charisma of this hero was overwhelming. Your famous nerves of steel became like wet pasta in his presense. As you stood there frozen the hero took aim and shot you through the heart.'

        elif self.persist['reaction'] is None and self.persist['enemy-reaction'] is None:
            if self.persist['hit']['by_player'] and self.persist['hit']['by_enemy']:
                # both dead
                self.persist['highscore']['draws'] += 1
                player_result = "It's a draw"
                if self.persist['player_character'] == 1:
                    player_comment = 'You both drew early trying to outwith the other. As a result you died, but by killing the outlaw you managed to save the town. They people in the town made a memorial shrine in your honor.'
                else:
                    player_comment = 'You tried to cheat but the hero was not playing fair either. As you let you shot go you see the hero get hit and go down. As you smile you feel a stinging pain and look down seeing the blood and your legacy dies there with you.'
            elif self.persist['hit']['by_player'] and not self.persist['hit']['by_enemy']:
                # player wins early draw
                player_result = 'You win'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['wins'] += 1
                    player_comment = 'You saved the town by killing the outlaw. People celebrate you return but what they do now know is that you shot early and caught the outlaw by suprise. These events will way upon you for the rest of your life.'
                else:
                    self.persist['highscore']['outlaw']['wins'] += 1
                    player_comment = 'The hero never stood a chance. You are a outlaw and the only thing that matters is that you keep standing. So you draw early and shot him before he knew what happend. The town is yours now.'
            elif not self.persist['hit']['by_player'] and self.persist['hit']['by_enemy']:
                # player dies early draw
                player_result = 'You loose'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['loses'] += 1
                    player_comment = 'You died even after trying to pull a fast one and shoot early. As you look up at the outlaw you see him tip his head to you for you effort but you both knew you never stood a chance.'
                else:
                    self.persist['highscore']['outlaw']['loses'] += 1
                    player_comment = 'You died even as you pulled early. You must have been sloppy and the hero pulled early as well. As you look up you see the hero his face hang down in shame even though the people cheer him om.'
            else:
                # stand off early draw
                player_result = "It's a draw"
                self.persist['highscore']['draws'] += 1
                if self.persist['player_character'] == 1:
                    player_comment = 'You drew early but the outlaw did as well. As the dust clears you are both are standing. As you stare off in the distance you here the towns people come to your aid. Your courage has inspired them and the outlaw high tailes it out of there.'
                else:
                    player_comment = 'You drew early but the hero did as well. As the dust clears you are both still standing. As you get ready to pull again you see the towns people come. You flee as it is no longer in your favor.'
        elif self.persist['reaction'] is None and self.persist['enemy-reaction']:
            if self.persist['hit']['by_player']:
                # player wins
                player_result = 'You win'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['wins'] += 1
                    player_comment = 'You saved the town by killing the outlaw. People celebrate your return and as the shindig goes on into the night. But you cannot enjoy the party knowing that you had to resort to cheating.'
                else:
                    self.persist['highscore']['outlaw']['wins'] += 1
                    player_comment = 'You are a outlaw and this town is yours. As the hero goes down you walk passed him and smile as he had played by the rules. That night as your boys take back the town its people tremble in fear for you.'
            elif self.persist['hit']['by_enemy']:
                # player looses
                player_result = 'You loose'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['loses'] += 1
                    player_comment = 'You died even after trying to pull a fast one and shoot early. As you look up at the outlaw you see him tip his head to you for you effort but you both knew you never stood a chance.'
                else:
                    self.persist['highscore']['outlaw']['loses'] += 1
                    player_comment = 'You died even as you pulled early. This hero was more then you are used to. He was unphased by your deceit and shot through. As you bleed out you hear the peoplecheer him om.'
            else:
                # it is a draw
                player_result = "It's a draw"
                self.persist['highscore']['draws'] += 1
                if self.persist['player_character'] == 1:
                    player_comment = 'You drew early and shot although you missed your drawing early put the outlaw enough on edge that he missed as well. As you are now at a stand off the towns people are coming to your aid making the outlaw hightail it out of there.'
                else:
                    player_comment = 'You drew early and shot although you missed your drawing early did make the hero sway and miss. As you get ready to shoot again you see the towns folk aproach and flee for safety.'
        elif self.persist['reaction'] and self.persist['enemy-reaction'] is None:
            if self.persist['hit']['by_player']:
                # player wins
                player_result = 'You win'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['wins'] += 1
                    player_comment = 'Even though the outlaw shot early he missed your heart kept true and killed the outlaw. People celebrate your return and as the shindig goes on into the night the bell of the ball asks you to dance. It is the start of something beautyfull.'
                else:
                    self.persist['highscore']['outlaw']['wins'] += 1
                    player_comment = 'You are a outlaw and this town is yours. As the hero goes down you tip your hat to him for trying to pull a fast one. To bad for him you have got nerves of steel. That night as your boys take back the town its people tremble in fear for you.'
            elif self.persist['hit']['by_enemy']:
                # player looses
                player_result = 'You loose'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['loses'] += 1
                    player_comment = 'You died and never stood a chance. He pulled on you before the coin hit the ground. Looking back you should have know this would happen. But how could you cheat you are a hero. The town is now at the outlaws mercy.'
                else:
                    self.persist['highscore']['outlaw']['loses'] += 1
                    player_comment = 'You die, the hero pulled early and caught you by suprise. You hear the people cheer him on as he looks away in disgrace on what he had to do. You leave this world knowing you left your mark on the hero his life.'
            else:
                # it is a draw
                player_result = "It's a draw"
                self.persist['highscore']['draws'] += 1
                if self.persist['player_character'] == 1:
                    player_comment = 'The outlaw drew early but still missed even though it rattled you enough to miss as well. As you are now at a stand off the towns people are coming to your aid making the outlaw hightail it out of there.'
                else:
                    player_comment = 'Even though the hero drew early his nervous made him miss. But this type of hero made you flinch and miss your reaction. As you get ready to shoot again you see the towns folk aproach and flee for safety.'
        elif self.persist['reaction'] < self.persist['enemy-reaction']:
            if self.persist['hit']['by_player']:
                # player wins
                player_result = 'You win'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['wins'] += 1
                    player_comment = 'Your shot was quicker then the outlaw and as he falls to the ground you see him reconzie your skills in his dying breath. You are the new gun in town. People celebrate your return and as the shindig goes on into the night the bell of the ball asks you to dance. It is the start of something beautyfull.'
                else:
                    self.persist['highscore']['outlaw']['wins'] += 1
                    player_comment = 'You have always and always will be the quickest gun. As the hero goes down you look at him with pitty. As you ride back into town you see your girl at the bar wave at you. That night as your boys take back the town its people tremble in fear for you as you share a bottle with your girl.'
            elif self.persist['hit']['by_enemy']:
                # player looses
                player_result = 'You loose'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['loses'] += 1
                    player_comment = 'You died and never stood a chance. Even though you are a quicker shot the outlaw has a better aim. Looking back you should have know this would happen. The town is now at the outlaws mercy.'
                else:
                    self.persist['highscore']['outlaw']['loses'] += 1
                    player_comment = 'You die, even though you pulled quicker the hero his aim was true. People where right you had lost your edge and now your life to the hero. You hear the people cheer him on as he gets embracced by the girl you had been trying to court while running the town.'
            else:
                # it is a draw
                player_result = "It's a draw"
                self.persist['highscore']['draws'] += 1
                if self.persist['player_character'] == 1:
                    player_comment = 'Even though your draw was quicker then the outlaw you missed. But this was enough to make him miss as well. As you are now at a stand off the towns people are coming to your aid making the outlaw hightail it out of there.'
                else:
                    player_comment = 'Even though you drew quicker then the hero you missed. But this was enough to make the heroflinch and miss . As you get ready to shoot again you see the towns folk aproach and flee for safety.'
        elif self.persist['reaction'] > self.persist['enemy-reaction']:
            if self.persist['hit']['by_player']:
                # player wins
                player_result = 'You win'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['wins'] += 1
                    player_comment = 'The outlaw was quicker in the draw but your aim was true and hit him. People celebrate your return and as the shindig goes on into the night the bell of the ball asks you to dance. It is the start of something beautyfull.'
                else:
                    self.persist['highscore']['outlaw']['wins'] += 1
                    player_comment = 'You may not be the quickest gun anymore you still are the best shot. As the hero goes down you look at him with pitty that he missed you with his shot. As you ride back into town you see your girl at the bar wave at you. That night as your boys take back the town its people tremble in fear for you as you share a bottle with your girl.'
            elif self.persist['hit']['by_enemy']:
                # player looses
                player_result = 'You loose'
                if self.persist['player_character'] == 1:
                    self.persist['highscore']['hero']['loses'] += 1
                    player_comment = 'You died and never stood a chance. The outlaw is truelly the fastes gun in the west. Looking back you should have know this would happen. The town is now at the outlaws mercy.'
                else:
                    self.persist['highscore']['outlaw']['loses'] += 1
                    player_comment = 'You die, the hero pulled quicker then you. People where right you had lost your edge and now your life to the hero. You hear the people cheer him on as he gets embracced by the girl you had been trying to court while running the town.'
            else:
                # it is a draw
                player_result = "It's a draw"
                self.persist['highscore']['draws'] += 1
                if self.persist['player_character'] == 1:
                    player_comment = 'Even though the outlaw was quicker he missed. But this was enough to make you miss as well. As you are now at a stand off the towns people are coming to your aid making the outlaw hightail it out of there.'
                else:
                    player_comment = 'Even though the hero drew quicker he missed you. But this was enough to make you flinch and miss . As you get ready to shoot again you see the towns folk aproach and flee for safety.'
        else:
            player_result = 'Unexpected outcome'
            player_comment = 'If you are reading this you broke the game. Oke you won. Happy now.'

        if self.persist['reaction'] and (self.persist['highscore']['quickest_draw'] is None or self.persist['highscore']['quickest_draw'] > self.persist['reaction']):
            self.persist['highscore']['quickest_draw'] = self.persist['reaction']
        self.player_result = f"{player_result} {'Hero' if self.persist['player_character'] == 1 else 'Outlaw'}"
        self.player_comment = player_comment
        self.render_text = self.player_comment
        self.draw_next_page = True
        save_highscore_data(self.persist['highscore'])

    def process_events(self, key_events, mouse_events):
        if key_events.get(pg.K_q) == 'released':
            pg.quit()
            sys.exit()

        if key_events.get(pg.K_SPACE) == 'released':
            if self.render_text:
                self.draw_next_page = True
            else:
                self.done = True
        if key_events.get(pg.K_RETURN) == 'released':
            self.done = True

    def update(self, dt):
        pass

    def draw(self, surface):
        if self.draw_next_page:
            surface.fill((0, 0, 0))
            surface.blit(self.font_big.render(self.player_result, False, (255, 255, 255)), (110, 0))
            self.render_text = draw_text(surface, self.render_text, (255, 255, 255), (110, 100, 800, 400), self.font)
            pg.draw.rect(surface, (255, 255, 255), (70, 90, 880, 400), width=3)
            if self.render_text:
                text_box_text = 'spacebar next page or enter to close'
            else:
                text_box_text = 'spacebar or enter to close'
            rendered_text = self.font_small.render(text_box_text, False, (200, 200, 200))
            surface.blit(rendered_text, (int(950 - rendered_text.get_rect().width), 500))
            self.draw_next_page = False
