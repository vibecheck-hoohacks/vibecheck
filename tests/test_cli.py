"""Tests for the CLI entry point and subcommands."""

from __future__ import annotations

from cli.main import build_parser


class TestBuildParser:
    def test_no_args_shows_help(self) -> None:
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_auth_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["auth"])
        assert args.command == "auth"

    def test_cm_init_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["cm", "init"])
        assert args.command == "cm"
        assert args.cm_command == "init"

    def test_cc_init_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["cc", "init"])
        assert args.command == "cc"
        assert args.cc_command == "init"
