
import asyncio
import discord
from discord.ext import commands
from functools import partial
import math
import os
import random

from utils import checks
from utils.dataIO import dataIO
from utils.chat_formatting import error, escape_mass_mentions, pagify, warning


# Constants
MAX_ROUNDS = 4
INITIAL_HP = 100
TARGET_SELF = 'self'
TARGET_OTHER = 'target'

DATA_PATH = "data/duel/"
JSON_PATH = DATA_PATH + "duelist.json"


def indicatize(d):
    result = {}
    for k, v in d.items():
        if k in VERB_IND_SUB:
            k = VERB_IND_SUB[k]
        else:
            k += 's'
        result[k] = v
    return result


# TEMPLATES BEGIN
# {a} is attacker, {d} is defender/target, {s} is a randomly selected object,
# {v} is the verb associated with that object, and {b} is a random body part.

WEAPONS = {}

MELEE = {
    'smash': {
        'elbow': 5
    },
    'drive': {
        'fist': 4,
        'toe': 2,
        'heel': 3
    },
    'gouge': {
        'finger': 4
    },
    'smack': {
        'palm': 3, 
        'backhand': 4
    }
    }    

MARTIAL = {'roundhouse kick': 6,
           'uppercut': 5,
           'bitch-slap': 2,
           'headbutt': 4}

STYLE_KARATE = {'karate chop': 5,
                'karate kick': 5,
                'straight punch': 3, 
                'hook': 3, 
                'side kick': 3}

STYLE_TAI_CHI = {}

STYLE_WRESTLING = {}

STYLE_BJJ = {}

STYLE_BOXING = {}

STYLE_KRAV_MAGA = {}

STYLE_SAMBO = {}

STYLE_MUAY_THAI = {}

STYLE_AIKIDO = {}

STYLE_JEETKUNDO = {}

STYLE_KUNGFU = {}

BODYPARTS = [
    'head',
    'eye socket', 
    'testicles', 
    'tits', 
    'tit',
    'ass',
    'liver', 
    'ribs',
    'temple',
    'ear',
    'throat',
    'neck',
    'solar plexus',
    'ribcage',
    'balls',
    'spleen',
    'kidney',
    'leg',
    'spine', 
    'arm',
    'jugular',
    'abdomen',
    'shin',
    'knee',
    'other knee'
]

VERB_IND_SUB = {'munch': 'munches', 'toss': 'tosses'}

ATTACK = {"{a} {v} their {s} at {d}!": indicatize(WEAPONS),
          "{a} {v} their {s} into {d}!": indicatize(MELEE),
          "{a} {v} their {s} into {d}'s {b}!": indicatize(MELEE),
          "{a} {v} {d}!": indicatize(MARTIAL),
          "{d} is bowled over by {a}'s sudden bull rush!": 6,
          "{a} tickles {d}, causing them to pass out from lack of breath": 2,
          "{a} points at something in the distance, distracting {d} long enough to {v} them!": MARTIAL
          }

CRITICAL = {"Quicker than the eye can follow, {a} delivers a devastating blow with their {s} to {d}'s {b}.": WEAPONS,
            "{a} nails {d} in the {b} with their {s}! Critical hit!": WEAPONS,
            "With frightening speed and accuracy, {a} devastates {d} with a tactical precision strike to the {b}. Critical hit!": WEAPONS
            }

HEALS = {
    'inject': {
        'morphine': 4,
        'nanomachines': 5
    },
    'smoke': {
        'a fat joint': 2,
        'medicinal incense': 3,
        'their hookah': 3
    },
    'munch': {
        'on some': {
            'cake': 5,
            'cat food': 3,
            'dog food': 4
        },
        'on a': {
            'waffle': 4,
            'turkey leg': 2
        }
    },
    'drink': {
        'some': {
            'Ambrosia': 7,
            'unicorn piss': 5,
            'purple drank': 2,
            'sizzurp': 3,
            'goon wine': 2
        },
        'a': {
            'generic hp potion': 5,
            'refreshingly delicious can of 7-Up': 3,
            'fresh mug of ale': 3
        },
        'an': {
            'elixir': 5
        }
    }
}

HEAL = {"{a} decides to {v} {s} instead of attacking.": HEALS,
        "{a} calls a timeout and {v} {s}.": indicatize(HEALS),
        "{a} decides to meditate on their round.": 5}


FUMBLE = {"{a} closes in on {d}, but suddenly remembers a funny joke and laughs instead.": 0,
          "{a} moves in to attack {d}, but is disctracted by a shiny.": 0,
          "{a} {v} their {s} at {d}, but has sweaty hands and loses their grip, hitting themself instead.": indicatize(WEAPONS),
          "{a} {v} their {s}, but fumbles and drops it on their {b}!": indicatize(WEAPONS)
          }

BOT = {"{a} charges its laser aaaaaaaand... BZZZZZZT! {d} is now a smoking crater for daring to challenge the bot.": INITIAL_HP}

HITS = ['deals', 'hits for']
RECOVERS = ['recovers', 'gains', 'heals']

# TEMPLATES END

# Move category target and multiplier (negative is damage)
MOVES = {
    'CRITICAL': (CRITICAL, TARGET_OTHER, -2),
    'ATTACK': (ATTACK, TARGET_OTHER, -1),
    'FUMBLE': (FUMBLE, TARGET_SELF, -1),
    'HEAL': (HEAL, TARGET_SELF, 1),
    'BOT': (BOT, TARGET_OTHER, -64)
}

# Weights of distribution for biased selection of moves
WEIGHTED_MOVES = {'CRITICAL': 0.05, 'ATTACK': 1, 'FUMBLE': 0.1, 'HEAL': 0.1}


class Player:
    def __init__(self, cog, member, initial_hp=INITIAL_HP):
        self.hp = initial_hp
        self.member = member
        self.mention = member.mention
        self.cog = cog

    # Using object in string context gives (nick)name
    def __str__(self):
        return self.member.display_name

    # helpers for stat functions
    def _set_stat(self, stat, num):
        stats = self.cog._get_stats(self)
        if not stats:
            stats = {'wins': 0, 'losses': 0, 'draws': 0}
        stats[stat] = num
        return self.cog._set_stats(self, stats)

    def _get_stat(self, stat):
        stats = self.cog._get_stats(self)
        return stats[stat] if stats and stat in stats else 0

    def get_state(self):
        return {k: self._get_stat(k) for k in ('wins', 'losses', 'draws')}

    # Race-safe, directly usable properties
    @property
    def wins(self):
        return self._get_stat('wins')

    @wins.setter
    def wins(self, num):
        self._set_stat('wins', num)

    @property
    def losses(self):
        return self._get_stat('losses')

    @losses.setter
    def losses(self, num):
        self._set_stat('losses', num)

    @property
    def draws(self):
        return self._get_stat('draws')

    @draws.setter
    def draws(self, num):
        self._set_stat('draws', num)


class Bullshido:
    def __init__(self, bot):
        self.bot = bot
        self.duelists = dataIO.load_json(JSON_PATH)
        self.underway = set()

    def _set_stats(self, user, stats):
        userid = user.member.id
        serverid = user.member.server.id

        if serverid not in self.duelists:
            self.duelists[serverid] = {}

        self.duelists[serverid][userid] = stats
        dataIO.save_json(JSON_PATH, self.duelists)

    def _get_stats(self, user):
        userid = user.member.id
        serverid = user.member.server.id
        if serverid not in self.duelists or userid not in self.duelists[serverid]:
            return None

        return self.duelists[serverid][userid]

    def get_player(self, user: discord.Member):
        return Player(self, user)

    def get_all_players(self, server: discord.Server):
        return [self.get_player(m) for m in server.members]

    def format_display(self, server, id):
        if id.startswith('r'):
            role = discord.utils.get(server.roles, id=id[1:])

            if role:
                return '@%s' % role.name
            else:
                return 'deleted role #%s' % id
        else:
            member = server.get_member(id)

            if member:
                return member.display_name
            else:
                return 'missing member #%s' % id

    def is_protected(self, member: discord.Member, member_only=False) -> bool:
        sid = member.server.id
        protected = set(self.duelists.get(sid, {}).get('protected', []))
        roles = set() if member_only else set('r' + r.id for r in member.roles)
        return member.id in protected or bool(protected & roles)

    def protect_common(self, obj, protect=True):
        if not isinstance(obj, (discord.Member, discord.Role)):
            raise TypeError('Can only pass member or role objects.')

        server = obj.server
        id = ('r' if type(obj) is discord.Role else '') + obj.id

        protected = self.duelists.get(server.id, {}).get("protected", [])

        if protect == (id in protected):
            return False
        elif protect:
            protected.append(id)
        else:
            protected.remove(id)

        if server.id not in self.duelists:
            self.duelists[server.id] = {}

        self.duelists[server.id]['protected'] = protected
        dataIO.save_json(JSON_PATH, self.duelists)
        return True

    @commands.group(name="protect", invoke_without_command=True, no_pm=True, pass_context=True)
    async def _protect(self, ctx, user: discord.Member):
        """
        Manage the protection list (adds items)
        """
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._protect_user, user)

    @_protect.command(name="me", pass_context=True)
    async def _protect_self(self, ctx):
        """
        Adds you to the bullshido protection list
        """
        sid = ctx.message.server.id
        self_protect = self.duelists.get(sid, {}).get('self_protect', False)
        author = ctx.message.author

        if self.is_protected(author, member_only=True):
            await self.bot.say("You're already in the protection list.")
            return
        elif self_protect is False:
            await self.bot.say('Sorry, self-protection is currently disabled.')
            return
        elif type(self_protect) is int:
            economy = self.bot.get_cog('Economy')

            if not economy:
                await self.bot.say(warning('The economy cog is not loaded.'))
                return
            elif not economy.bank.account_exists(author):
                await self.bot.say(warning("You don't have a bank account yet."))
                return
            elif not economy.bank.can_spend(author, self_protect):
                await self.bot.say("You don't have %i credits to spend." % self_protect)
                return

            try:
                economy.bank.withdraw_credits(author, self_protect)
            except Exception as e:
                self.bot.logger.exception(e)
                await self.bot.say(error("Transaction failed. Bot owner: check the logs."))
                return

        if self.protect_common(ctx.message.author, True):
            await self.bot.say("You have been successfully added to the protection list.")
        else:
            await self.bot.say("Something went wrong adding you to the protection list.")

    @checks.admin_or_permissions(administrator=True)
    @_protect.command(name="price", pass_context=True)
    async def _protect_price(self, ctx, param: str = None):
        """
        Enable, disable, or set the price of self-protection

        Valid options: "disable", "free", or any number 0 or greater.
        """
        sid = ctx.message.server.id
        current = self.duelists.get(sid, {}).get('self_protect', False)

        if param:
            param = param.lower().strip(' "`')

            if param in ('disable', 'none'):
                param = False
            elif param in ('free', '0'):
                param = True
            elif param.isdecimal():
                param = int(param)
            else:
                await self.bot.send_cmd_help(ctx)
                return

        if param is None:
            adj = 'currently'
            param = current
        elif param == current:
            adj = 'already'
        else:
            adj = 'now'

            if sid not in self.duelists:
                self.duelists[sid] = {'self_protect': param}
            else:
                self.duelists[sid]['self_protect'] = param

            dataIO.save_json(JSON_PATH, self.duelists)

        if param is False:
            disp = 'disabled'
        elif param is True:
            disp = 'free'
        elif type(param) is int:
            disp = 'worth %i credits' % param
        else:
            raise RuntimeError('unhandled param value, please report this bug!')

        msg = 'Self-protection is %s %s.' % (adj, disp)
        economy = self.bot.get_cog('Economy')

        if type(param) is int and not economy:
            msg += '\n\n' + warning('NOTE: the economy cog is not loaded. Members '
                                    'will not be able to purchase protection.')

        await self.bot.say(msg)

    @checks.mod_or_permissions(administrator=True)
    @_protect.command(name="user", pass_context=True)
    async def _protect_user(self, ctx, user: discord.Member):
        """Adds a member to the protection list"""
        if self.protect_common(user, True):
            await self.bot.say("%s has been successfully added to the protection list." % user.display_name)
        else:
            await self.bot.say("%s is already in the protection list." % user.display_name)

    @checks.admin_or_permissions(administrator=True)
    @_protect.command(name="role", pass_context=True)
    async def _protect_role(self, ctx, role: discord.Role):
        """Adds a role to the protection list"""
        if self.protect_common(role, True):
            await self.bot.say("The %s role has been successfully added to the protection list." % role.name)
        else:
            await self.bot.say("The %s role is already in the protection list." % role.name)

    @commands.group(name="unprotect", invoke_without_command=True, no_pm=True, pass_context=True)
    async def _unprotect(self, ctx, user: discord.Member):
        """
        Manage the protection list (removes items)
        """
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._unprotect_user, user)

    @checks.mod_or_permissions(administrator=True)
    @_unprotect.command(name="user", pass_context=True)
    async def _unprotect_user(self, ctx, user: discord.Member):
        """Removes a member from the bullshido protection list"""
        if self.protect_common(user, False):
            await self.bot.say("%s has been successfully removed from the protection list." % user.display_name)
        else:
            await self.bot.say("%s is not in the protection list." % user.display_name)

    @checks.admin_or_permissions(administrator=True)
    @_unprotect.command(name="role", pass_context=True)
    async def _unprotect_role(self, ctx, role: discord.Role):
        """Removes a role from the bullshido protection list"""
        if self.protect_common(role, False):
            await self.bot.say("The %s role has been successfully removed from the protection list." % role.name)
        else:
            await self.bot.say("The %s role is not in the protection list." % role.name)

    @_unprotect.command(name="me", pass_context=True)
    async def _unprotect_self(self, ctx):
        """Removes you from the bullshido protection list"""
        if self.protect_common(ctx.message.author, False):
            await self.bot.say("You have been removed from the protection list.")
        else:
            await self.bot.say("You aren't in the protection list.")

    @commands.command(name="protected", pass_context=True, aliases=['protection'])
    async def _protection(self, ctx):
        """Displays the bullshido protection list"""
        server = ctx.message.server
        duelists = self.duelists.get(server.id, {})
        member_list = duelists.get("protected", [])
        fmt = partial(self.format_display, server)

        if member_list:
            name_list = map(fmt, member_list)
            name_list = ["**Protected users and roles:**"] + sorted(name_list)
            delim = '\n'

            for page in pagify(delim.join(name_list), delims=[delim]):
                await self.bot.say(escape_mass_mentions(page))
        else:
            await self.bot.say("The list is currently empty, add users or roles with `%sprotect` first." % ctx.prefix)

    @commands.group(name="bullshido", pass_context=True, allow_dms=False)
    async def _bullshido(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._duels_list)

    @_bullshido.command(name="list", pass_context=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def _bullshido_list(self, ctx, top: int = 10):
        """Shows the bullshido leaderboard, defaults to top 10"""
        server = ctx.message.server
        server_members = {m.id for m in server.members}

        if top < 1:
            top = 10

        if server.id in self.duelists:
            def sort_wins(kv):
                _, v = kv
                return v['wins'] - v['losses']

            def stat_filter(kv):
                uid, stats = kv

                if type(stats) is not dict or uid not in server_members:
                    return False

                return True

            # filter out extra data, TODO: store protected list seperately
            duel_stats = filter(stat_filter, self.duelists[server.id].items())
            duels_sorted = sorted(duel_stats, key=sort_wins, reverse=True)

            if not duels_sorted:
                await self.bot.say('No records to show.')
                return

            if len(duels_sorted) < top:
                top = len(duels_sorted)

            topten = duels_sorted[:top]
            highscore = ""
            place = 1
            members = {uid: server.get_member(uid) for uid, _ in topten}  # only look up once each
            names = {uid: m.nick if m.nick else m.name for uid, m in members.items()}
            max_name_len = max([len(n) for n in names.values()])

            # header
            highscore += '#'.ljust(len(str(top)) + 1)  # pad to digits in longest number
            highscore += 'Name'.ljust(max_name_len + 4)

            for stat in ['wins', 'losses', 'draws']:
                highscore += stat.ljust(8)

            highscore += '\n'

            for uid, stats in topten:
                highscore += str(place).ljust(len(str(top)) + 1)  # pad to digits in longest number
                highscore += names[uid].ljust(max_name_len + 4)

                for stat in ['wins', 'losses', 'draws']:
                    val = stats[stat]
                    highscore += '{}'.format(val).ljust(8)

                highscore += "\n"
                place += 1
            if highscore:
                if len(highscore) < 1985:
                    await self.bot.say("```py\n" + highscore + "```")
                else:
                    await self.bot.say("The leaderboard is too big to be displayed. Try with a lower <top> parameter.")
        else:
            await self.bot.say("There are no scores registered in this server. Start fighting!")

    @checks.admin_or_permissions(administrator=True)
    @_bullshido.command(name="reset", pass_context=True)
    async def _bullshido_reset(self, ctx):
        "Clears duel scores without resetting protection or editmode."
        keep_keys = {'protected', 'edit_posts', 'self_protect'}
        sid = ctx.message.server.id
        data = self.duelists.get(sid, {})
        dks = set(data.keys())

        if dks <= keep_keys:
            await self.bot.say('Nothing to reset.')
            return

        keep_data = {k: data[k] for k in keep_keys & dks}
        self.duelists[sid] = keep_data
        dataIO.save_json(JSON_PATH, self.duelists)
        await self.bot.say('Duel records cleared.')

    @checks.admin_or_permissions(administrator=True)
    @_bullshido.command(name="editmode", pass_context=True)
    async def _bullshido_postmode(self, ctx, on_off: bool = None):
        "Edits messages in-place instead of posting each move seperately."
        sid = ctx.message.server.id
        current = self.duelists.get(sid, {}).get('edit_posts', False)

        if on_off is None:
            adj = 'enabled' if current else 'disabled'
            await self.bot.say('In-place editing is currently %s.' % adj)
            return

        adj = 'enabled' if on_off else 'disabled'
        if on_off == current:
            await self.bot.say('In-place editing already %s.' % adj)
        else:
            if sid not in self.duelists:
                self.duelists[sid] = {}

            self.duelists[sid]['edit_posts'] = on_off
            await self.bot.say('In-place editing %s.' % adj)

        dataIO.save_json(JSON_PATH, self.duelists)

    @_bullshido.command(name="duel", pass_context=True, no_pm=True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def _(self, ctx, user: discord.Member):
        """Duel another player"""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        duelists = self.duelists.get(server.id, {})

        abort = True

        if channel.id in self.underway:
            await self.bot.say("There's already a duel underway in this channel!")
        elif user == author:
            await self.bot.reply("you can't duel yourself, silly!")
        elif self.is_protected(author):
            await self.bot.reply("you can't duel anyone while you're on the protected users list.")
        elif self.is_protected(user):
            await self.bot.reply("%s is on the protected users list." % user.display_name)
        else:
            abort = False

        if abort:
            bucket = ctx.command._buckets.get_bucket(ctx)
            bucket._tokens += 1  # Sorry, Danny
            return

        p1 = Player(self, author)
        p2 = Player(self, user)
        self.underway.add(channel.id)

        try:
            self.bot.dispatch('duel', channel=channel, players=(p1, p2))

            order = [(p1, p2), (p2, p1)]
            random.shuffle(order)
            msg = ["%s challenges %s to a duel!" % (p1, p2)]
            msg.append("\nBy a coin toss, %s will go first." % order[0][0])
            msg_object = await self.bot.say('\n'.join(msg))
            for i in range(MAX_ROUNDS):
                if p1.hp <= 0 or p2.hp <= 0:
                    break
                for attacker, defender in order:
                    if p1.hp <= 0 or p2.hp <= 0:
                        break

                    if attacker.member == ctx.message.server.me:
                        move_msg = self.generate_action(attacker, defender, 'BOT')
                    else:
                        move_msg = self.generate_action(attacker, defender)

                    if duelists.get('edit_posts', False):
                        new_msg = '\n'.join(msg + [move_msg])
                        if len(new_msg) < 2000:
                            await self._robust_edit(msg_object, content=new_msg)
                            msg = msg + [move_msg]
                            await asyncio.sleep(1)
                            continue

                    msg_object = await self.bot.say(move_msg)
                    msg = [move_msg]
                    await asyncio.sleep(1)

            if p1.hp != p2.hp:
                victor = p1 if p1.hp > p2.hp else p2
                loser = p1 if p1.hp < p2.hp else p2
                victor.wins += 1
                loser.losses += 1
                msg = 'After {0} rounds, {1.mention} wins with {1.hp} HP!'.format(i + 1, victor)
                msg += '\nStats: '

                for p, end in ((victor, '; '), (loser, '.')):
                    msg += '{0} has {0.wins} wins, {0.losses} losses, {0.draws} draws{1}'.format(p, end)
            else:
                victor = None

                for p in [p1, p2]:
                    p.draws += 1

                msg = 'After %d rounds, the duel ends in a tie!' % (i + 1)

            await self.bot.say(msg)
            self.bot.dispatch('duel_completion', channel=channel, players=(p1, p2), victor=victor)
        except Exception:
            raise
        finally:
            self.underway.remove(channel.id)

    def generate_action(self, attacker, defender, move_cat=None):
        # Select move category
        if not move_cat:
            move_cat = weighted_choice(WEIGHTED_MOVES)

        # Break apart move info
        moves, target, multiplier = MOVES[move_cat]

        target = defender if target is TARGET_OTHER else attacker

        move, strike, verb, hp_delta = self.generate_move(moves)
        hp_delta *= multiplier
        bodypart = random.choice(BODYPARTS)

        msg = move.format(a=attacker, d=defender, s=strike, v=verb, b=bodypart)
        if hp_delta == 0:
            pass
        else:
            target.hp += hp_delta
            if hp_delta > 0:
                s = random.choice(RECOVERS)
                msg += ' It %s %d HP (%d)' % (s, abs(hp_delta), target.hp)
            elif hp_delta < 0:
                s = random.choice(HITS)
                msg += ' It %s %d damage (%d)' % (s, abs(hp_delta), target.hp)

        return msg

    def generate_move(self, moves):
        # Select move, action, object, etc
        movelist = nested_random(moves)
        hp_delta = movelist.pop()  # always last
        # randomize damage/healing done by -/+ 33%
        hp_delta = math.floor(((hp_delta * random.randint(66, 133)) / 100))
        move = movelist.pop(0)  # always first
        verb = movelist.pop(0) if movelist else None  # Optional
        obj = movelist.pop() if movelist else None  # Optional

        if movelist:
            verb += ' ' + movelist.pop()  # Optional but present when obj is

        return move, obj, verb, hp_delta

    async def _robust_edit(self, msg, content=None, embed=None):
        try:
            msg = await self.bot.edit_message(msg, new_content=content, embed=embed)
        except discord.errors.NotFound:
            msg = await self.bot.send_message(msg.channel, content=content, embed=embed)
        except Exception:
            raise

        return msg

    async def on_command(self, command, ctx):
        if ctx.cog is self and self.analytics:
            self.analytics.command(ctx)


def weighted_choice(choices):
    total = sum(w for c, w in choices.items())
    r = random.uniform(0, total)
    upto = 0

    for c, w in choices.items():
        if upto + w >= r:
            return c

        upto += w


def nested_random(d):
    k = weighted_choice(dict_weight(d))
    result = [k]

    if type(d[k]) is dict:
        result.extend(nested_random(d[k]))
    else:
        result.append(d[k])

    return result


def dict_weight(d, top=True):
    wd = {}
    sw = 0

    for k, v in d.items():
        if isinstance(v, dict):
            x, y = dict_weight(v, False)
            wd[k] = y if top else x
            w = y
        else:
            w = 1
            wd[k] = w

        sw += w

    if top:
        return wd
    else:
        return wd, sw


def check_folders():
    if os.path.exists("data/duels/"):
        os.rename("data/duels/", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        print("Creating data/duel folder...")
        os.mkdir(DATA_PATH)


def check_files():
    if not dataIO.is_valid_json(JSON_PATH):
        print("Creating duelist.json...")
        dataIO.save_json(JSON_PATH, {})


async def setup(bot):
    check_folders()
    check_files()
    await bot.add_cog(Bullshido(bot))
