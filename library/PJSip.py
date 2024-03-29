#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#https://github.com/MartyTremblay/sip2mqtt/blob/master/sip2mqtt.py
#https://github.com/alyssaong1/VoIPBot/blob/master/src/runclient.py
#https://github.com/cristeab/autodialer/blob/master/core/softphone.py
#https://github.com/crs4/most-voip/blob/master/python/src/most/voip/api_backend.py
#https://github.com/pjsip/pjproject/issues/3125
#https://gist.github.com/hu55a1n1/6d00be6316013fdde5e5ed20549ebbef


__app__ = "PJSip"
__VERSION__ = "0.2"
__DATE__ = "31.07.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import time

import pjsua2 as pj
import logging
import sys



# mod2 creates its own logger, as a sub logger to 'spam'
logger = logging.getLogger('pjsua.mod2')

notification = False
callState = False
logHandle = False
outerClassObject = False




class PJSip(object):

  #  callState = None
    def __init__(self,logger,p_pipeIn):
  #  def __init__(self,callback,root_logger):
      #  self._calbackk = callbackz

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        global logHandle
        logHandle = self._log
        global outerClassObject
        outerClassObject = self


        self._log.debug('Create PJSip mqttclient Object')
        self._ep = None
        self._acc = None

        self._host = None
        self._port = 5060

        self._debugLevel = 4

        self._call = None

        self._pipe = p_pipeIn


    class MyLogWriter(pj.LogWriter):
        def write(self, entry):
            print("Logger:", entry.msg)






    class MyCall(pj.Call):

        def __init__(self, acc, peer_uri='', chat=None, call_id=pj.PJSUA_INVALID_ID):
            pj.Call.__init__(self, acc, call_id)
            self.acc = acc
            self.wav_player = None
            self.wav_recorder = None
            print('Create MyCall object')

            global notification

        def __enter__(self):
            print('Create MyCall obejct')

        def __exit__(self, exc_type, exc_val, exc_tb):
            print('Closing MyCall', exc_type,exc_val,exc_tb)

        def __del__(self):
            print("DELETE Call Object")


        def onCallStateNew(self, prm):
            ci = self.getInfo()
            self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED
            self.recorder = None
            if (self.connected == True):
                player = pj.AudioMediaPlayer()
                # Play welcome message
                player.createPlayer("temp/announcement.wav");

                self.recorder = pj.AudioMediaRecorder()
                self.recorder.createRecorder('temp/file.wav', enc_type=0, max_size=0,
                                             options=0);
                i = 0
                for media in ci.media:

                    if (media.type == pj.PJMEDIA_TYPE_AUDIO):
                        self.aud_med = self.getMedia(i);
                        break;
                    i = i + 1;
                if self.aud_med != None:
                    # This will connect the sound device/mic to the call audio media
                    mym = pj.AudioMedia.typecastFromMedia(self.aud_med)
                    player.startTransmit(mym);
                    # mym.startTransmit( self.recorder);
            if (ci.state == pj.PJSIP_INV_STATE_DISCONNECTED):
                print(">>>>>>>>>>>>>>>>>>>>>>> Call disconnected")
                # mym= pj.AudioMedia.typecastFromMedia(self.aud_med)
                # mym.stopTransmit(self.recorder);
            raise Exception('onCallState done!')

            # override the function at original parent class
        # parent class's function can be called by super().onCallState()
        def onCallState(self, prm):
            global callState
            print('onCallState')

            ci = self.getInfo()
            print("*** Call: {} [{}]".format(ci.remoteUri, ci.lastStatusCode))
            if ci.lastStatusCode == 404:
                print("call can't established with code 404!")
                # quitPJSUA()
            if ci.state == pj.PJSIP_INV_STATE_CALLING:
                print('***CALLIJG***', ci.lastStatusCode)
                notification({
                    "INFO":"CALLING",
                    "STATUS Code": ci.lastStatusCode
                })

            if ci.state == pj.PJSIP_INV_STATE_CONNECTING:
                print('***CONNECTING***', ci.lastStatusCode)
                notification({
                    "INFO":"CONNECTING",
                    "STATUS Code": ci.lastStatusCode
                })

            if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
                print('***CONFIRMED***', ci.lastStatusCode)
                notification({
                    "INFO":"CONFIREMDE",
                    "STATUS Code": ci.lastStatusCode
                })

                print(ci.media, ci.media[0], ci.media.size)
                if ci.media[0].type == pj.PJMEDIA_TYPE_AUDIO:
                    print('***AUDIO***')
                    notification({
                        "INFO": "AUDIO CAll",
                        "STATUS Code": ci.lastStatusCode
                    })
                if ci.media[0].status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print('***MEDIA ACTIVE***')
                    notification({
                        "INFO": "AUDIO ACTIVE",
                        "STATUS Code": ci.lastStatusCode
                    })
                    aud_med = None

                    try:
                        # get the "local" media
                        aud_med = self.getAudioMedia(-1)
                        print('Aud_med', aud_med)

                    except pj.Error as e:
                        print("exception!!: {}".format(e.args))

                    if not self.wav_player:
                        #self.wav_player = pj.AudioMediaPlayer()
                        self.wav_player = pj.AudioMediaPlayer()
                        try:
                            self.wav_player.createPlayer("temp/announcement.wav",pj.PJMEDIA_FILE_NO_LOOP)
                            aud_med = self.getAudioMedia(-1)
                            print('player created', aud_med)
                        #   self.wav_player.startTransmit(aud_med)
                        except pj.Error as e:
                            print("Exception!!: failed opening wav file")
                            del self.wav_player
                            self.wav_player = None
                        else:
                            print('Start playbacksss')
                        #   self.wav_player.startTransmit(aud_med)
                    if self.wav_player:
                        #print('play message')
                        notification({
                            "INFO": "PLAY MESSAGE",
                            "STATUS Code": ci.lastStatusCode
                        })
                        self.wav_player.startTransmit(aud_med)
                        notification({
                            "INFO": "PLAY MESSAGE COMPLETED",
                            "STATUS Code": ci.lastStatusCode
                        })
                        #print('Message played completed')

            if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                print('***DISCONNECTING***', ci.lastStatusCode)
                notification({
                    "INFO": "DISCONNECTING",
                    "STATUS Code": ci.lastStatusCode
                })
                callState = 'CLOSE'

        def onDtmfDigit(self, prm):
            print('Received DTMF', prm.digit)
            notification({
                "INFO": "DTMF RECEIVED",
                "DTMF": prm.digit
            })

        def onCallMediaStateOld(self, prm):
            ci = self.getInfo()
            print('TEST',ci,prm)

            for mi in ci.media:
                print('TEST2',ci.media.size(), mi)
                if mi.type == pj.PJMEDIA_TYPE_AUDIO:
                    print('pj.PJMEDIA_TYPE_AUDIO')
                if mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print('ACTIVE')



            aud_med = None

            try:
                # get the "local" media
                aud_med = self.getAudioMedia(-1)
                print('Aud_med',aud_med)
            except pj.Error as e:
                print("exception!!: {}".format(e.args))


            if not self.wav_player:
                self.wav_player = pj.AudioMediaPlayer()
                try:
                    self.wav_player.createPlayer("./input.16.wav")
                    aud_med = self.getAudioMedia(-1)
                    print('player created',aud_med)
                 #   self.wav_player.startTransmit(aud_med)
                except pj.Error as e:
                    print("Exception!!: failed opening wav file")
                    del self.wav_player
                    self.wav_player = None
                else:
                    print('Start playbacksss')
                 #   self.wav_player.startTransmit(aud_med)
            if self.wav_player:
                print('play message')
                self.wav_player.startTransmit(aud_med)

    class MyMediaPlayer(pj.AudioMediaPlayer):
        def __init__(self):
            print('INIT-------------------------------------------')
            super().__init__()

        def onEof2(self):
            print('playback completed')
            notification({
                "INFO": "Message Played"
            })

        def play_file(self, audio_media: pj.AudioMedia, sound_file_name: str) -> None:
            print('play_file')
            notification({
                "INFO": "Play Message"
            })

    class MyAccount(pj.Account):
        def __init__(self,callObj):
            self._callObj = callObj
            pj.Account.__init__(self)
            self._cfg = pj.AccountConfig()
            print('Account info', self._cfg)
           # pj.Account.__init__(self, account)
            global notification

        def onRegState(self, prm):
           # global notification
            print("***OnRegState: ", prm.reason)
       #     self._log.info("***OnRegState: %s" % prm.reason)
            notification(prm.reason)
        #    self._notification('**OnState' + str(prm.reason))
         #   self.accountState = prm.reason

        def onIncomingCall(self, prm):
            c = self._callObj(self, call_id=prm.callId)
            call_prm = pj.CallOpParam()
            call_prm.statusCode = 180
            c.answer(call_prm)
            ci = c.getInfo()
            print('CI',ci)
            print('CI Remote',ci.remoteUri)
            print('CI URI',self._cfg.idUri)
            # Unless this callback is implemented, the default behavior is to reject the call with default status code.
            #self._log.info("SIP: Incoming call from " + ci.remoteUri())
            notification({
                "INFO":"Incomming Call",
                "MSG": ci.remoteUri
            })
            time.sleep(3)
            call_prm.statusCode =200
            c.answer(call_prm)
           # broker.publish(args.mqtt_topic, payload="{\"verb\": \"incoming\", \"caller\":\"" + extract_caller_id(
            #    call.info().remote_uri) + "\", \"uri\":" + json.dumps(call.info().remote_uri) + "}", qos=0, retain=True)

          #  current_call = call
         #   print(call.info())
            #call_cb = SMCallCallback(current_call)
            #current_call.set_callback(call_cb)

    def callNumber(self,id:str) -> bool:
        global callState

        uri = 'sip:' + id +'@' + self._host + ':' + str(self._port)

       # calls=['sip:0795678728@192.168.2.1:5060']
        print('Call URI ', uri, self._call)

        self._call = self.MyCall(self._acc)

        self._prm = pj.CallOpParam(True)
        self._prm.opt.audioCount = 1
        self._prm.opt.videoCount = 0

        print('make call', callState, self._prm)
        self._call.makeCall(uri, self._prm)
      #  print(callState != 'CLOSE')
        while callState != 'CLOSE':
            self._ep.libHandleEvents(100)
           # print('CallState:',callState)
      #  while True:
       #     self._ep.libHandleEvents(10)
        # while True:
        #    if end > time.time():
        #       pj.Endpoint.instance().libHandleEvents(20)
        callState = False
        print('-done--')
       # self._ep.hangupAllCalls()
        self.hangup()
        del self._call
        self._call = None


    def hangup(self):
        self._ep.hangupAllCalls()

    def setNotification(self,sink: str) -> bool:
        self._log.debug('setNotification %s'% sink)
        global notification
        notification = self.notifier
        notification('TEST')
        return True

    def notifier(self,msg):
        self._pipe.send(msg)
        print('send messgage',msg)

    def logNotification(self,msg: str) -> bool:
        self._log.debug('PJSipLog: %s'%msg)
        return True

    def setDebugLevel(self,level: int)->bool:
        self_debugLevel = level
        return True

    def setupAccount(self,host: str,user: str ,passwd: str) -> bool:

        self._host = host

        # init the lib
     #   self._ep = pj.Endpoint()
      #  self._ep.libCreate()


       # lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))
        #https://stackoverflow.com/questions/62095804/calling-pj-thread-register-from-python
        self._ep_cfg = pj.EpConfig()
        # Python does not like PJSUA2's thread. It will result in segment fault
        self._ep_cfg.uaConfig.threadCnt = 1
        self._ep_cfg.uaConfig.mainThreadOnly = True
        #self._ep.libRegisterThread("PJSUA-THREAD")
       # print('***REGISTER***',self._ep.libIsThreadRegistered())

        #Debug
        #self._ep_cfg.logConfig.writer = Logger()
       # self._ep_cfg.logConfig.filename = "pjsua.log"
        #self._ep_cfg.logConfig.fileFlags = pj.PJ_O_APPEND
        self._ep_cfg.logConfig= pj.LogConfig()
       # self._ep_cfg.logConfig.writer = Logger()
      #  self._ep_cfg.logConfig.decor = self._ep_cfg.logConfig.decor & ~(pj.PJ_LOG_HAS_CR | pj.PJ_LOG_HAS_NEWLINE)
       # self._ep_cfg.logConfig.level = 4
        #self._ep_cfg.logConfig.consoleLevel = 5

        lw = self.MyLogWriter()
        self._ep_cfg.logConfig.writer = lw
        self._ep_cfg.logConfig.decor = self._ep_cfg.logConfig.decor & ~(pj.PJ_LOG_HAS_CR | pj.PJ_LOG_HAS_NEWLINE)


       # self._ep_cfg.logConfig.decor = self._ep_cfg.logConfig.decor & ~(pj.PJ_LOG_HAS_CR | pj.PJ_LOG_HAS_NEWLINE)
        #log_cfg = pj.LogConfig(level=3, callback=log_cb)
       # w = MyLogWriter()
       # ep_cfg.logConfig.writer = l._log

        # using thread in python may cause some problem
       # self._ep_cfg.uaConfig.threadCnt = 1
       # self._ep_cfg.uaConfig.mainThreadOnly = True

        self._ep = pj.Endpoint()
        self._ep.libCreate()

        try:
            self._ep.libInit(self._ep_cfg)
        except:
            print('ERROR Init lib')


        # add some config
        tcfg = pj.TransportConfig()
        # tcfg.port = 5060
        try:
            self._ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg)
        except:
            print('ERROR Transport')
        # add account config
        self._acc_cfg = pj.AccountConfig()
        self._acc_cfg.idUri = 'sip:{}@{}'.format(user,host)

        print("*** start sending SIP REGISTER ***")
        self._acc_cfg.regConfig.registrarUri = 'sip:' + host

        # if there needed credential to login, just add following lines
        cred = pj.AuthCredInfo("digest", "*", user, 0, passwd)
        self._acc_cfg.sipConfig.authCreds.append(cred)

        self._acc = self.MyAccount(self.MyCall)
        self._acc.create(self._acc_cfg)
        # acc = pj.Account()
        # acc.create(acc_cfg)

        try:
            self._ep.libStart()
            print("*** PJSUA2 STARTED ***")
        except:
            print('ERROR Start Lib')


      #  self._notification('STARTED')
      #  self._ep.utilLogWriter(3,'TEST','TEST')

        # use null device as conference bridge, instead of local sound card
        pj.Endpoint.instance().audDevManager().setNullDev()
        print('*** Complete ***')
        while True:
        #    print('?')
            self._ep.libHandleEvents(10)
         #   print('!')
           # pj.Endpoint.instance().libHandleEvents(20)
            #x = self._pipe.recv()
            #x = self._pipe.get()
            if self._pipe.poll():
                print('Poll')
                msg = self._pipe.recv()
                print('X',msg)
                self.callNumber(msg)

        return

    def shutdown(self):
        self._ep.libDestroy()



