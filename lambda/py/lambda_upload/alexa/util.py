# -*- coding: utf-8 -*-

import random
import feedparser
import logging
import requests
import atoma

from typing import List, Dict
from ask_sdk_model import IntentRequest, Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, StopDirective)
from ask_sdk_core.handler_input import HandlerInput
from . import data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_rss_data():
    resp = requests.get(data.AUDIO_RSS)
    feed_data = atoma.parse_rss_bytes(resp.content)
    return feed_data.items

def get_playback_info(handler_input):
    # type: (HandlerInput) -> Dict
    persistence_attr = handler_input.attributes_manager.persistent_attributes
    return persistence_attr.get('playback_info')

def get_current_track(handler_input):
    playback_info = get_playback_info(handler_input)

    feed_data = get_rss_data()
    current_id = playback_info.get("current_id")

    if(not current_id):
        return feed_data[0]
    
    for track in feed_data:
        if(track.guid == current_id):
            return track
    
    return feed_data[0]

def get_next_track(handler_input):
    playback_info = get_playback_info(handler_input)

    feed_data = get_rss_data()
    current_id = playback_info.get("current_id")

    if(not current_id):
        return feed_data[0]

    feed_length = len(feed_data)
    
    #start at 1
    for number, track in enumerate(feed_data, start=1):
        if(track.guid == current_id):
            if(feed_length > number):
                return feed_data[number]
            else:
                return feed_data[0]
    
    return feed_data[0]

def get_previous_track(handler_input):
    playback_info = get_playback_info(handler_input)

    feed_data = get_rss_data()
    current_id = playback_info.get("current_id")

    if(not current_id):
        return feed_data[0]
    
    for number, track in enumerate(feed_data, start=1):
        if(track.guid == current_id):
            if(track == 1):
                return feed_data[0]
            else:
                return feed_data[number - 2] #start begins at 1
    
    return feed_data[0]

def can_throw_card(handler_input):
    # type: (HandlerInput) -> bool
    playback_info = get_playback_info(handler_input)
    if (isinstance(handler_input.request_envelope.request, IntentRequest)
            and playback_info.get('playback_index_changed')):
        playback_info['playback_index_changed'] = False
        return True
    else:
        return False


def get_token(handler_input):
    """Extracting token received in the request."""
    # type: (HandlerInput) -> str
    return handler_input.request_envelope.request.token



def get_offset_in_ms(handler_input):
    """Extracting offset in milliseconds received in the request"""
    # type: (HandlerInput) -> int
    return handler_input.request_envelope.request.offset_in_milliseconds


class Controller:
    """Audioplayer and Playback Controller."""
    @staticmethod
    def play(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        playback_info = get_playback_info(handler_input)
        response_builder = handler_input.response_builder

        offset_in_ms = playback_info.get("offset_in_ms")
        podcast = get_current_track(handler_input)

        play_behavior = PlayBehavior.REPLACE_ALL
        playback_info['next_stream_enqueued'] = False

        response_builder.add_directive(
            PlayDirective(
                play_behavior=play_behavior,
                audio_item=AudioItem(
                    stream=Stream(
                        token=podcast.guid,
                        url=podcast.enclosures[0].url,
                        offset_in_milliseconds=offset_in_ms,
                        expected_previous_token=None),
                    metadata=None))
        ).set_should_end_session(True)

        if not is_playback:
            # Add card and response only for events not triggered by
            # Playback Controller
            handler_input.response_builder.speak(
                data.PLAYBACK_PLAY.format(podcast.title))

            if can_throw_card(handler_input):
                response_builder.set_card(SimpleCard(
                    title=data.PLAYBACK_PLAY_CARD.format(
                        podcast.title),
                    content=data.PLAYBACK_PLAY_CARD.format(
                        podcast.title)))

        return response_builder.response

    @staticmethod
    def stop(handler_input):
        # type: (HandlerInput) -> Response
        handler_input.response_builder.add_directive(StopDirective())
        return handler_input.response_builder.response

    @staticmethod
    def play_next(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        persistent_attr = handler_input.attributes_manager.persistent_attributes

        playback_info = persistent_attr.get("playback_info")
        playback_setting = persistent_attr.get("playback_setting")
        next_track = get_next_track(handler_input)

        playback_info["current_id"] = next_track.guid
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True

        return Controller.play(handler_input, is_playback)

    @staticmethod
    def play_previous(handler_input, is_playback=False):
        # type: (HandlerInput) -> Response
        persistent_attr = handler_input.attributes_manager.persistent_attributes

        playback_info = persistent_attr.get("playback_info")
        playback_setting = persistent_attr.get("playback_setting")
        prev_track = get_previous_track(handler_input)

        playback_info["current_id"] = prev_track.guid
        playback_info["offset_in_ms"] = 0
        playback_info["playback_index_changed"] = True

        return Controller.play(handler_input, is_playback)
