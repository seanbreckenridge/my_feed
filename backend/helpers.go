package main

import (
	"strconv"
	"time"
)

func contains(slice []string, s string) bool {
	for _, item := range slice {
		if item == s {
			return true
		}
	}
	return false
}

// function which takes a min and max and makes sure user input is between them
func clamp(min int, max *int, val int) int {
	if val < min {
		return min
	}
	if max != nil && val > *max {
		return *max
	}
	return val
}

// https://go.dev/doc/faq#convert_slice_of_interface
func stringToInterface(s []string) []interface{} {
	i := make([]interface{}, len(s))
	for j, v := range s {
		i[j] = v
	}
	return i
}

func getEpochTime() string {
	return strconv.FormatInt(time.Now().Unix(), 10)
}
