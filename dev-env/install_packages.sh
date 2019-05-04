#!/bin/sh
pacstrap $1 base base-devel vim grub gnome \
      gcc git pypy jdk-openjdk kotlin \
      firefox gnome-tweaks noto-fonts noto-fonts-cjk \
      emacs geany kate gvim \
      pycharm-community-edition codeblocks \
      eclipse-java intellij-idea-community-edition
